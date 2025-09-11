Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Take screenshot
[System.Windows.Forms.SendKeys]::SendWait('%{PRTSC}')
Start-Sleep 2

# Get image from clipboard
$img = [Windows.Forms.Clipboard]::GetImage()
if ($img -ne $null) {
    $img.Save('C:\Users\joaop\Documents\Hobbies\Claude Night Writer\screenshot.png', [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host 'Screenshot saved to screenshot.png'
} else {
    Write-Host 'No image in clipboard'
}