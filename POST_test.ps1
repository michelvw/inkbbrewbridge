$url = "http://127.0.0.1:5000/api/v1/resources/temperatures"

$data =@{
 "temperature" = 18.19
 "measuredatetime" = Get-Date -UFormat "%Y-%m-%d %T"
}

$body = $data | ConvertTo-Json

Invoke-RestMethod -Uri $url -Body $body -ContentType "application/json" -Method Post