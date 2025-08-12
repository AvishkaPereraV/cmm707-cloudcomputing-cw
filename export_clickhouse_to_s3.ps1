# ============================
# Export ClickHouse data to CSV and upload to S3 (UTF-8)
# ============================

# --- Settings ---
$PodName = (kubectl get pods -o jsonpath="{.items[?(@.metadata.labels.app=='clickhouse')].metadata.name}")
$S3Bucket = "lugx-bucket"
$S3Key = "events_utf8.csv"
$ClickhouseUser = "default"
$ClickhousePass = "mypassword"

# --- Step 1: Export from ClickHouse to CSV inside the pod ---
Write-Host "Exporting data from ClickHouse..."
$Query = "SELECT event_type, page_url, user_agent, session_id, ts FROM analytics.events FORMAT CSVWithNames"
kubectl exec $PodName -- sh -c "clickhouse-client --user $ClickhouseUser --password $ClickhousePass --query='$Query' | iconv -f UTF-8 -t UTF-8 > /tmp/events_utf8.csv"

# --- Step 2: Copy file from pod to local folder ---
Write-Host "Copying file to local machine..."
cd "C:\Users\Savindri Perera\Documents\CloudComputingCW"
kubectl cp "${PodName}:/tmp/events_utf8.csv" "events_utf8.csv"

# --- Step 3: Upload to S3 ---
Write-Host "Uploading to S3..."
aws s3 cp "events_utf8.csv" "s3://$S3Bucket/$S3Key" --region us-east-1

# --- Step 4: Confirmation ---
if ($LASTEXITCODE -eq 0) {
    Write-Host "Export + Upload Complete!"
} else {
    Write-Host "Something went wrong!"
}
