from app.core import s3_client, settings


# expires in: 86400 (24h)
def generate_presigned_url(object_key: str, expires_in: int = 86400) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": object_key,
        },
        ExpiresIn=expires_in,
    )
