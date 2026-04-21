from datetime import datetime, timedelta, timezone
import io
import re
import uuid
from typing import Any

import pdfplumber
from minio import Minio
from litestar.datastructures import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import spacy
except Exception:  # pragma: no cover - dépendance optionnelle en runtime
    spacy = None

from config.settings import settings
from features.applications.model import PartialApplication
from features.candidates.schemas import CandidateProfileRequest, CandidateResponse
from features.candidates.exceptions import CandidateNotFoundError


class CandidateService:
    _SKILL_KEYWORDS: dict[str, str] = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "sql": "SQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "react": "React",
        "vue": "Vue",
        "angular": "Angular",
        "django": "Django",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "git": "Git",
        "linux": "Linux",
    }

    _SECTION_STOP_RE = re.compile(
        r"^(summary|profil|profile|education|formation|projects?|projets?|certifications?|lang(?:u)?ages?|skills?|comp[eé]tences?|experience|exp[eé]riences?)\b",
        re.IGNORECASE,
    )

    def __init__(self, minio_client: Minio):
        self._minio = minio_client
        self._nlp: Any | None = None
        self._spacy_load_attempted = False

    async def get_profile(self, candidate_id: str) -> CandidateResponse:
        raise NotImplementedError

    async def upsert_profile(self, user_id: str, payload: CandidateProfileRequest) -> CandidateResponse:
        raise NotImplementedError

    async def list_candidates(self, page: int = 1, page_size: int = 20) -> list[CandidateResponse]:
        raise NotImplementedError

    async def _validate_pdf(self, upload_file: UploadFile) -> bool:
        # Vérifier l'extension
        if not upload_file.filename.lower().endswith(".pdf"):
            raise ValueError("Le fichier n'est pas un PDF. Veuillez téléverser votre CV au format PDF.")

        # Vérifier les magic bytes
        first_bytes = await upload_file.read(4)
        if not first_bytes.startswith(b"%PDF"):
            raise ValueError("Le fichier n'est pas un PDF valide. Veuillez téléverser votre CV au format PDF.")

        # Remettre le curseur au début
        try:
            await upload_file.seek(0)
        except Exception:
            try:
                upload_file.file.seek(0)
            except Exception:
                pass

        return True

    async def _parse_pdf(self, upload_file: UploadFile) -> str:
        """Parse le PDF et extrait le texte brut"""
        try:
            # Assurer que le curseur est au début
            try:
                await upload_file.seek(0)
            except Exception:
                try:
                    upload_file.file.seek(0)
                except Exception:
                    pass

            pdf = pdfplumber.open(upload_file.file)
            raw_text = ""

            for page in pdf.pages:
                text = page.extract_text()
                if text:  # Verifions si la page est vide
                    raw_text += text + "\n"

            pdf.close()

            # Remettre le curseur pour d'éventuelles opérations suivantes
            try:
                upload_file.file.seek(0)
            except Exception:
                pass

            return raw_text.strip()
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing du PDF: {str(e)}")

    def _generate_ai_question(self, raw_text: str) -> str:
        """Générer une question d'entretien à partir du texte du CV.

        Ceci est une implémentation de placeholder. Remplacer par une
        intégration réelle d'IA (OpenAI, Azure, etc.) si nécessaire.
        """
        # Simple heuristique : si des compétences connues apparaissent, poser une question ciblée
        skills_keywords = ["python", "javascript", "docker", "aws", "sql", "react", "django", "fastapi"]
        lower = raw_text.lower()
        for kw in skills_keywords:
            if kw in lower:
                return f"Pouvez-vous décrire un projet où vous avez utilisé {kw} et les défis rencontrés ?"

        # Sinon question générique
        return "Parlez-nous de votre expérience la plus significative et des résultats obtenus."

    def _get_spacy_nlp(self) -> Any | None:
        """Charge spaCy en lazy-loading; retourne None en fallback silencieux."""
        if self._spacy_load_attempted:
            return self._nlp

        self._spacy_load_attempted = True
        if spacy is None:
            return None

        try:
            self._nlp = spacy.load(settings.SPACY_MODEL)
        except Exception:
            self._nlp = None
        return self._nlp

    @staticmethod
    def _clean_and_dedupe(items: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            value = re.sub(r"\s+", " ", item).strip("\t\r\n -:;,.•")
            if len(value) < 2:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(value)

        return cleaned

    def _extract_name_line(self, lines: list[str]) -> str:
        """Trouve une ligne plausible de nom dans les premières lignes du CV."""
        candidate_lines = lines[:6]
        for line in candidate_lines:
            lower = line.lower()
            if "@" in line:
                continue
            if "http://" in lower or "https://" in lower or "www." in lower or "linkedin" in lower:
                continue
            if sum(char.isdigit() for char in line) >= 4:
                continue
            if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$", line):
                continue

            words = [w for w in line.split() if w]
            if 2 <= len(words) <= 5:
                return " ".join(words)

        return ""

    def _extract_section_lines(self, lines: list[str], heading_re: re.Pattern[str]) -> list[str]:
        section_lines: list[str] = []
        capture = False

        for line in lines:
            if capture and self._SECTION_STOP_RE.match(line):
                break

            if capture:
                section_lines.append(line)
                continue

            if heading_re.match(line):
                capture = True

        return section_lines

    def _extract_skills(self, lines: list[str], raw_text: str) -> list[str]:
        heading_re = re.compile(r"^(skills?|comp[eé]tences?)\b[:\s-]*$", re.IGNORECASE)
        section_lines = self._extract_section_lines(lines, heading_re)

        extracted: list[str] = []
        for line in section_lines:
            extracted.extend(re.split(r"[,;|/•\-]", line))

        normalized: list[str] = []
        for token in extracted:
            cleaned = re.sub(r"\(.*?\)", "", token).strip()
            key = cleaned.lower()
            if key in self._SKILL_KEYWORDS:
                normalized.append(self._SKILL_KEYWORDS[key])
            elif 2 <= len(cleaned) <= 40:
                normalized.append(cleaned)

        if not normalized:
            lower_text = raw_text.lower()
            for keyword, display in self._SKILL_KEYWORDS.items():
                if re.search(rf"\b{re.escape(keyword)}\b", lower_text):
                    normalized.append(display)

        return self._clean_and_dedupe(normalized)

    def _extract_experiences(self, lines: list[str], raw_text: str) -> list[str]:
        heading_re = re.compile(r"^(experience|experiences|exp[eé]riences?)\b[:\s-]*$", re.IGNORECASE)
        section_lines = self._extract_section_lines(lines, heading_re)

        experiences: list[str] = []
        for line in section_lines:
            if len(line) >= 20:
                experiences.append(line)

        if not experiences:
            year_re = re.compile(r"\b(?:19|20)\d{2}(?:\s*[-/]\s*(?:19|20)?\d{2})?\b")
            for line in lines:
                if year_re.search(line):
                    experiences.append(line)
                if len(experiences) >= 5:
                    break

        if not experiences:
            experiences = [segment.strip() for segment in raw_text.split("\n\n") if len(segment.strip()) > 30][:3]

        return self._clean_and_dedupe(experiences[:5])

    @staticmethod
    def _extract_email(raw_text: str) -> str | None:
        email_match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            raw_text,
            flags=re.IGNORECASE,
        )
        if not email_match:
            return None
        return email_match.group(0).strip().lower()

    @staticmethod
    def _extract_phone(raw_text: str) -> str | None:
        phone_pattern = re.compile(
            r"(?:\+|00)?\d[\d\s()./-]{7,}\d",
            flags=re.IGNORECASE,
        )
        for match in phone_pattern.finditer(raw_text):
            candidate = match.group(0).strip()
            digits = re.sub(r"\D", "", candidate)
            if len(digits) < 8 or len(digits) > 15:
                continue
            return candidate
        return None

    def _extract_structured_fields(self, raw_text: str) -> dict[str, Any]:
        """Extrait des champs structurés (heuristiques + enrichissement spaCy)."""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        full_name = self._extract_name_line(lines)
        skills = self._extract_skills(lines, raw_text)
        experiences = self._extract_experiences(lines, raw_text)

        nlp = self._get_spacy_nlp()
        if nlp is not None:
            try:
                doc = nlp(raw_text[:20000])

                if not full_name:
                    person_entities = [
                        ent.text.strip()
                        for ent in doc.ents
                        if ent.label_.upper() in {"PERSON", "PER"} and 2 <= len(ent.text.split()) <= 5
                    ]
                    if person_entities:
                        full_name = person_entities[0]

                if not experiences:
                    sentence_candidates: list[str] = []
                    for sent in doc.sents:
                        sentence = sent.text.strip()
                        if re.search(r"\b(?:19|20)\d{2}\b", sentence) and len(sentence) >= 20:
                            sentence_candidates.append(sentence)
                        if len(sentence_candidates) >= 5:
                            break
                    experiences = self._clean_and_dedupe(sentence_candidates)
            except Exception:
                # En cas d'erreur NLP, on conserve uniquement les heuristiques.
                pass

        first_name = ""
        last_name = ""
        if full_name:
            name_parts = full_name.split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        email = self._extract_email(raw_text)
        telephone = self._extract_phone(raw_text)

        return {
            "full_name": full_name or None,
            "first_name": first_name or None,
            "last_name": last_name or None,
            "email": email,
            "telephone": telephone,
            "skills": skills,
            "experiences": experiences,
        }

    @staticmethod
    def _build_dated_cv_object_path(candidate_id: str, current_time: datetime | None = None) -> str:
        now = current_time or datetime.now(timezone.utc)
        iso_week = now.isocalendar().week
        return f"cvs/{now:%Y/%m}/W{iso_week:02d}/{now:%d}/{candidate_id}/cv.pdf"

    async def _create_partial_application(
        self,
        db_session: AsyncSession,
        job_id: str,
        cv_obj: str,
        structured_fields: dict[str, Any],
    ) -> PartialApplication:
        partial_application = PartialApplication(
            id=str(uuid.uuid4()),
            person_uid=uuid.uuid4().hex,
            job_id=job_id,
            nom=structured_fields.get("last_name"),
            prenom=structured_fields.get("first_name"),
            email=structured_fields.get("email"),
            telephone=structured_fields.get("telephone"),
            cv_obj=cv_obj,
        )
        db_session.add(partial_application)
        await db_session.commit()
        return partial_application

    async def check_authorization(self, candidate_id: str, job_id: str | None = None) -> dict:
        """Vérifie si la candidature du `candidate_id` est autorisée pour un `job_id` optionnel.

        Retourne un dict avec `authorized: bool` et `reason: str | None`.
        Actuellement, logique par défaut : autorisée sauf si l'ID contient 'banned' ou 'blocked'.
        Remplacer par logique métier / DB réelle si disponible.
        """
        # Placeholder rules
        if "banned" in candidate_id or "blocked" in candidate_id:
            return {"candidate_id": candidate_id, "authorized": False, "reason": "Candidat banni"}

        # Exemple : si job_id fourni, appliquer règles supplémentaires (placeholder)
        if job_id and job_id.startswith("internal-"):
            return {"candidate_id": candidate_id, "authorized": False, "reason": "Offre interne: candidature non autorisée"}

        return {"candidate_id": candidate_id, "authorized": True, "reason": None}

    async def process_and_store_cv(
        self,
        upload_file: UploadFile,
        candidate_id: str,
        db_session: AsyncSession | None = None,
    ) -> dict:
        """Valide, parse et stocke le PDF brut + texte parsé dans MinIO.

        Retourne les chemins/URLs des objets stockés.
        """
        await self._validate_pdf(upload_file)
        raw_text = await self._parse_pdf(upload_file)
        structured_fields = self._extract_structured_fields(raw_text)

        bucket = settings.MINIO_BUCKET
        pdf_obj = self._build_dated_cv_object_path(candidate_id)
        # Préparer et uploader le PDF brut (seul l'objet PDF est stocké dans MinIO)
        file_obj = upload_file.file
        try:
            file_obj.seek(0, io.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(0)
        except Exception:
            # si on ne peut pas déterminer la taille, lire en mémoire
            content = await upload_file.read()
            size = len(content)
            file_obj = io.BytesIO(content)

        # put_object attend un file-like et la longueur
        self._minio.put_object(bucket, pdf_obj, file_obj, size)

        # Le texte parsé n'est PAS stocké dans MinIO : il reste traité côté API.
        # Générer une question proposée par l'IA (placeholder)
        ai_question = self._generate_ai_question(raw_text)
        # Générer URL présignée pour le PDF (valable 24h)
        try:
            cv_url = self._minio.presigned_get_object(bucket, pdf_obj, expires=timedelta(hours=24))
        except Exception:
            cv_url = ""

        partial_application_id = None
        person_uid = None
        if db_session is not None:
            partial_application = await self._create_partial_application(
                db_session=db_session,
                job_id=candidate_id,
                cv_obj=pdf_obj,
                structured_fields=structured_fields,
            )
            partial_application_id = partial_application.id
            person_uid = partial_application.person_uid

        return {
            "candidate_id": candidate_id,
            "cv_obj": pdf_obj,
            "cv_url": cv_url,
            "preview": raw_text[:500],
            "pages": None,
            "size_bytes": size,
            "full_name": structured_fields["full_name"],
            "first_name": structured_fields["first_name"],
            "last_name": structured_fields["last_name"],
            "email": structured_fields["email"],
            "telephone": structured_fields["telephone"],
            "skills": structured_fields["skills"],
            "experiences": structured_fields["experiences"],
            "partial_application_id": partial_application_id,
            "person_uid": person_uid,
            "ai_question": ai_question,
        }
