import boto3

# TODO Hide this in env variables

S3_BUCKET = "flask-trucks"  # os.environ.get("S3_BUCKET_NAME")
S3_KEY = "AKIASZZUIN7DDCNAWCXO"  # os.environ.get("S3_ACCESS_KEY")
S3_SECRET = "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"  # os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)


def upload_file_to_s3(file, folder, file_name=None, bucket_name=S3_BUCKET, acl="public-read"):
    try:
        if not file_name:
            file_name = file.filename
        file_name = file_name.replace(" ", "")
        s3.upload_fileobj(
            file,
            bucket_name,
            folder + '/' + file_name,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e

    return "{}{}".format(S3_LOCATION, folder + '/' + file_name)
