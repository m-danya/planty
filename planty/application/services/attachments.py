# TODO: limit file uploading for each user

from typing import Any
import uuid

from aiobotocore.session import AioSession

from planty.config import settings


async def generate_presigned_post_url(
    s3_session: AioSession,
) -> tuple[str, dict[str, Any], str]:
    file_key = str(uuid.uuid4())

    async with s3_session.create_client(
        "s3",
        endpoint_url=settings.aws_url,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_access_key_id=settings.aws_access_key_id,
    ) as client:
        post_info = await client.generate_presigned_post(
            Bucket=settings.aws_attachments_bucket,
            Key=file_key,
            ExpiresIn=3600,  # 1 hour
            Conditions=[
                ["starts-with", "$Content-Disposition", ""],
                ["content-length-range", 0, 50 * 1048576],  # max 50 MiB
            ],
        )
        return post_info["url"], post_info["fields"], file_key
        # get_url=f"{settings.aws_url}/{settings.aws_attachments_bucket}/{file_key}",


# TODO: move to tests (+ configure test minio env)
# async def test_attachments_service() -> None:
#     a = AttachmentService()
#     urls = await a.get_presigned_url_for_uploading()
#     print(f"{urls = }")
#     response = httpx.post(
#         urls.post_url,
#         data={
#             **urls.post_fields,
#             "Content-Disposition": 'attachment; filename="shrek.txt"',
#         },
#         files={"file": ("filename", b"some content")},
#     )
#     assert response.is_success
#     response = httpx.get(urls.get_url)
#     assert response.is_success
