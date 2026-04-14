from typing import Optional
from datetime import datetime, timedelta, timezone
import io

import pdfplumber
from minio import Minio
from litestar.datastructures import UploadFile

from config.settings import settings
from features.candidates.schemas import CandidateProfileRequest, CandidateResponse
from features.candidates.exceptions import CandidateNotFoundError


class CandidateService:
    def __init__(self, minio_client: Optional[Minio] = None):
        # Use injected client when provided, otherwise create one on demand
        if minio_client is None:
            self._minio = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_SECURE,
            )
            try:
                if not self._minio.bucket_exists(settings.MINIO_BUCKET):
                    self._minio.make_bucket(settings.MINIO_BUCKET)
            except Exception:
                pass
        else:
            self._minio = minio_client
            # S'assurer que le bucket existe même si le client est injecté (utile pour les tests d'intégration)
            try:
                if not self._minio.bucket_exists(settings.MINIO_BUCKET):
                    self._minio.make_bucket(settings.MINIO_BUCKET)
            except Exception:
                pass

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

    async def process_and_store_cv(self, upload_file: UploadFile, candidate_id: str) -> dict:
        """Valide, parse et stocke le PDF brut + texte parsé dans MinIO.

        Retourne les chemins/URLs des objets stockés.
        """
        await self._validate_pdf(upload_file)
        raw_text = await self._parse_pdf(upload_file)

        bucket = settings.MINIO_BUCKET
        pdf_obj = f"cvs/{candidate_id}/cv.pdf"
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

        # Le texte parsé n'est PAS stocké dans MinIO : il est envoyé directement
        # au modèle/servicede traitement pour générer la question.
        # (La team Data doit fournir l'intégration réelle.)
        # Générer métadonnées locales
        metadata = {
            "candidate_id": candidate_id,
            "parsed_at": datetime.now(timezone.utc).isoformat(),
            "word_count": len(raw_text.split()),
        }
        # Générer une question proposée par l'IA (placeholder)
        ai_question = self._generate_ai_question(raw_text)
        # Générer URL présignée pour le PDF (valable 24h)
        try:
            cv_url = self._minio.presigned_get_object(bucket, pdf_obj, expires=timedelta(hours=24))
        except Exception:
            cv_url = ""

        return {
            "candidate_id": candidate_id,
            "cv_obj": pdf_obj,
            "cv_url": cv_url,
            "preview": raw_text[:500],
            "pages": None,
            "size_bytes": size,
            "ai_question": ai_question,
        }
