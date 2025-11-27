import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from uuid import uuid4
from datetime import datetime, timedelta

from app.core.config import settings


class StorageService:
    """
    S3-compatible storage service for file uploads.

    Supports AWS S3, Cloudflare R2, and other S3-compatible providers.
    """

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def generate_unique_key(self, filename: str, org_id: str) -> str:
        """
        Generate unique S3 key for file.

        Args:
            filename: Original filename
            org_id: Organization ID

        Returns:
            Unique S3 key
        """
        # Extract file extension
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''

        # Generate unique key with organization prefix
        unique_id = str(uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d')

        return f"{org_id}/{timestamp}/{unique_id}.{ext}"

    def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        org_id: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to S3.

        Args:
            file_obj: File object to upload
            filename: Original filename
            org_id: Organization ID
            content_type: MIME type

        Returns:
            S3 file URL

        Raises:
            Exception: If upload fails
        """
        key = self.generate_unique_key(filename, org_id)

        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )

            # Generate file URL
            if settings.S3_ENDPOINT_URL:
                # For Cloudflare R2 or custom endpoints
                return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{key}"
            else:
                # For AWS S3
                return f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{key}"

        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def generate_presigned_upload_url(
        self,
        filename: str,
        org_id: str,
        expiration: int = 3600
    ) -> dict:
        """
        Generate presigned URL for direct upload from client.

        This is the recommended approach for large files:
        1. Client requests presigned URL from API
        2. Client uploads directly to S3
        3. Client notifies API of completion

        Args:
            filename: Original filename
            org_id: Organization ID
            expiration: URL expiration in seconds (default 1 hour)

        Returns:
            Dict with url and key
        """
        key = self.generate_unique_key(filename, org_id)

        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )

            return {
                'url': url,
                'key': key,
                'expires_at': datetime.utcnow() + timedelta(seconds=expiration)
            }

        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def generate_presigned_download_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for file download.

        Args:
            key: S3 object key
            expiration: URL expiration in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")

    def delete_file(self, key: str) -> None:
        """
        Delete file from S3.

        Args:
            key: S3 object key

        Raises:
            Exception: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
        except ClientError as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    def get_file(self, key: str) -> bytes:
        """
        Download file from S3.

        Args:
            key: S3 object key

        Returns:
            File content as bytes

        Raises:
            Exception: If download fails
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()

        except ClientError as e:
            raise Exception(f"Failed to download file: {str(e)}")


# Global storage service instance
storage_service = StorageService()
