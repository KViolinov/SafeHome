<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checked Images from Firebase</title>
    <style>
        .image-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .image-container img {
            max-width: 200px;
            max-height: 200px;
            border: 1px solid #ccc;
            padding: 5px;
        }
    </style>
</head>
<body>
    <h1>Images in "checkedImages" Folder</h1>
    <div class="image-container">
        <?php
        // Firebase Storage bucket name
        $bucketName = "safehome-c4576.appspot.com";
        $folder = "checkedPhotos";

        // API URL to list items in the folder
        $url = "https://firebasestorage.googleapis.com/v0/b/$bucketName/o?prefix=$folder/";

        // Initialize cURL session
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        // Execute cURL request
        $response = curl_exec($ch);

        // Check for cURL errors
        if(curl_errno($ch)) {
            echo "cURL Error: " . curl_error($ch);
        } else {
            $data = json_decode($response, true);

            // Check if items exist
            if (isset($data['items'])) {
                foreach ($data['items'] as $item) {
                    // Generate the download URL for each item
                    $fileName = $item['name'];
                    $imageUrl = "https://firebasestorage.googleapis.com/v0/b/$bucketName/o/" . urlencode($fileName) . "?alt=media";
                    
                    // Display the image
                    echo "<img src='$imageUrl' alt='Image from Firebase Storage'>";
                }
            } else {
                echo "<p>No images found in 'checkedImages' folder.</p>";
            }
        }

        // Close cURL session
        curl_close($ch);
        ?>
    </div>
</body>
</html>
