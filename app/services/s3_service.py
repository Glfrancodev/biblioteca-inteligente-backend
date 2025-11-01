import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile, HTTPException
import os
from datetime import datetime
import uuid
from typing import Optional


class S3Service:
    """Servicio para interactuar con AWS S3"""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()  # Asegurar que las variables estén cargadas
        
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-2")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            print("⚠️ Advertencia: Credenciales de AWS S3 no configuradas")
            print(f"AWS_ACCESS_KEY_ID: {'✓' if self.aws_access_key_id else '✗'}")
            print(f"AWS_SECRET_ACCESS_KEY: {'✓' if self.aws_secret_access_key else '✗'}")
            print(f"AWS_BUCKET_NAME: {'✓' if self.bucket_name else '✗'}")
            raise ValueError("Faltan credenciales de AWS S3 en las variables de entorno")
        
        # Cliente de S3
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            print(f"✅ Cliente S3 inicializado correctamente para bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ Error al inicializar cliente S3: {str(e)}")
            raise
    
    def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "libros",
        custom_filename: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Sube un archivo a S3 y retorna la key y URL firmada
        
        Args:
            file: Archivo a subir
            folder: Carpeta dentro del bucket
            custom_filename: Nombre personalizado (opcional)
        
        Returns:
            tuple[str, str]: (s3_key, signed_url)
        """
        try:
            # Validar tipo de archivo
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="Solo se permiten archivos PDF"
                )
            
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            if custom_filename:
                # Limpiar nombre personalizado
                clean_name = custom_filename.replace(" ", "_").lower()
                filename = f"{clean_name}_{timestamp}_{unique_id}.pdf"
            else:
                # Usar nombre original
                original_name = file.filename.replace(" ", "_").lower()
                filename = f"{timestamp}_{unique_id}_{original_name}"
            
            # Key completa en S3
            s3_key = f"{folder}/{filename}"
            
            # Leer contenido del archivo
            file_content = file.file.read()
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType='application/pdf',
                ContentDisposition='inline'  # Para visualizar en navegador
            )
            
            # Resetear el puntero del archivo
            file.file.seek(0)
            
            print(f"✅ Archivo subido exitosamente: {s3_key}")
            
            # Generar URL firmada (válida por 7 días)
            signed_url = self.generate_presigned_url(s3_key, expiration=604800)
            
            return s3_key, signed_url
            
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="Credenciales de AWS no configuradas correctamente"
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al subir archivo a S3: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error inesperado: {str(e)}"
            )
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 604800) -> str:
        """
        Genera una URL firmada para acceder a un archivo en S3
        
        Args:
            s3_key: Key del archivo en S3
            expiration: Tiempo de expiración en segundos (default: 7 días)
        
        Returns:
            str: URL firmada
        """
        try:
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return signed_url
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al generar URL firmada: {str(e)}"
            )
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Elimina un archivo de S3
        
        Args:
            s3_key: Key del archivo en S3
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            print(f"🗑️ Archivo eliminado: {s3_key}")
            return True
        except ClientError as e:
            print(f"⚠️ Error al eliminar archivo: {str(e)}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Verifica si un archivo existe en S3
        
        Args:
            s3_key: Key del archivo en S3
        
        Returns:
            bool: True si existe
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False


# Instancia singleton del servicio
s3_service = S3Service()
