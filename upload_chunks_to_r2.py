"""
Upload chunked lookup files to R2 in parallel.
"""
import os
import boto3
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# R2 credentials from environment
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = 'ai-ecosystem-graph'

def upload_file(file_path, s3_client):
    """Upload a single file to R2"""
    try:
        # Get relative path from components/
        r2_key = file_path.replace('components/', '')
        
        with open(file_path, 'rb') as f:
            s3_client.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=r2_key,
                Body=f,
                ContentType='application/gzip',
                ContentEncoding='gzip'
            )
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return (r2_key, file_size_mb, True)
    except Exception as e:
        return (file_path, 0, False, str(e))

def upload_chunks():
    """Upload all chunk files to R2 in parallel"""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("Error: R2 credentials not found in environment variables")
        print("Please set: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
        return
    
    # Initialize S3 client for R2
    s3_client = boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )
    
    # Find all chunk files
    chunks_dir = 'components/chunks'
    chunk_files = [os.path.join(chunks_dir, f) for f in os.listdir(chunks_dir) 
                   if f.startswith('lookup_') and f.endswith('.json.gz')]
    
    # Also upload chunks_index.json.gz
    chunks_index = 'components/chunks_index.json.gz'
    if os.path.exists(chunks_index):
        chunk_files.append(chunks_index)
    
    print(f"Found {len(chunk_files)} files to upload")
    print("Uploading in parallel (20 workers)...")
    
    uploaded = 0
    failed = 0
    total_size = 0
    
    # Upload in parallel with 20 workers
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(upload_file, f, s3_client): f for f in chunk_files}
        
        for future in as_completed(futures):
            result = future.result()
            if result[2]:  # Success
                uploaded += 1
                total_size += result[1]
                if uploaded % 100 == 0:
                    print(f"  Uploaded {uploaded}/{len(chunk_files)} files ({total_size:.2f} MB)...")
            else:
                failed += 1
                print(f"  Failed: {result[0]} - {result[3] if len(result) > 3 else 'Unknown error'}")
    
    print(f"\n✓ Upload complete:")
    print(f"  Uploaded: {uploaded} files")
    print(f"  Failed: {failed} files")
    print(f"  Total size: {total_size:.2f} MB")

if __name__ == '__main__':
    upload_chunks()

