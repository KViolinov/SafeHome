<?php
session_start();

// Firebase configuration URLs
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json');
define('FIREBASE_DEVICE_LINKS_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json');
define('FIREBASE_MESSAGES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/messages.json');
define('FIREBASE_RESULTS_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/results.json');
define('FIREBASE_CAMERA_INFO_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/camera_info.json');

// Function to handle Firebase requests
function firebaseRequest($url, $method = 'GET', $data = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    if ($method == 'POST' || $method == 'PUT' || $method == 'DELETE') {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    }

    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function getCheckedPhotos($macAddress) {
    $folder = 'checkedPhotos/';
    $url = FIREBASE_BUCKET_URL . urlencode($folder) . "?alt=media";

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    if(curl_errno($ch)) {
        echo "Error: " . curl_error($ch);
        return [];
    }

    $data = json_decode($response, true);
    $images = [];

    // Loop through each image and filter by MAC address and timestamp
    foreach ($data['items'] as $item) {
        $fileName = $item['name'];
        $fileParts = explode('_', $fileName);

        // Expecting filename format: macAddress_date_month_hour_minute_second.jpg
        if (count($fileParts) >= 6) {
            list($fileMac, $day, $month, $hour, $minute, $second) = array_slice($fileParts, 0, 6);

            // Only include files that match the current device's MAC address
            if ($fileMac === $macAddress) {
                $imageUrl = "https://firebasestorage.googleapis.com/v0/b/safehome-c4576.appspot.com/o/" . urlencode($fileName) . "?alt=media";
                $images[] = ['url' => $imageUrl, 'timestamp' => "$hour:$minute:$second on $day/$month"];
            }
        }
    }

    curl_close($ch);
    return $images;
}

// Remove device link if "remove" action is requested
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['remove_mac'])) {
    $macToRemove = $_POST['remove_mac'];
    $firebaseDeleteUrl = FIREBASE_DEVICE_LINKS_URL . '/' . urlencode($macToRemove) . '.json';
    firebaseRequest($firebaseDeleteUrl, 'DELETE');
    header('Location: ' . $_SERVER['PHP_SELF']);
    exit();
}

// Fetch all user devices, device links, camera info, and messages from Firebase
$userDevices = firebaseRequest(FIREBASE_USER_DEVICES_URL);
$deviceLinks = firebaseRequest(FIREBASE_DEVICE_LINKS_URL);
$cameraInfo = firebaseRequest(FIREBASE_CAMERA_INFO_URL);
$messages = firebaseRequest(FIREBASE_MESSAGES_URL);
$results = firebaseRequest(FIREBASE_RESULTS_URL);

// Get the logged-in username
$username = isset($_SESSION['username']) ? $_SESSION['username'] : null;
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeHome - Dashboard</title>
    <link rel="stylesheet" href="style.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f7fc;
        }

        .container {
            display: flex;
            justify-content: space-between;
            gap: 30px;
            padding: 30px;
        }

        header {
            background-color: #34495e;
            padding: 20px;
            color: #fff;
            text-align: center;
        }

        header nav ul {
            list-style: none;
            padding: 0;
        }

        header nav ul li {
            display: inline;
            margin-right: 20px;
        }

        header nav ul li a {
            color: #fff;
            text-decoration: none;
            font-weight: bold;
        }

        h1 {
            text-align: center;
            color: #333;
        }

        .device-list,
        .messages {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 48%;
        }

        .device-list table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .device-list th,
        .device-list td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .device-list th {
            background-color: #f7f7f7;
        }

        .device-list td iframe {
            width: 100%;
            height: 300px;
            border: none;
        }

        .remove-button {
            background-color: #e74c3c;
            color: #fff;
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .edit-button {
            background-color: #1abc9c;
            color: #fff;
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .remove-button:hover {
            background-color: #c0392b;
        }

        .edit-button:hover {
            background-color: #15947b;
        }

        .messages ul {
            list-style-type: none;
            padding: 0;
        }

        .messages ul li {
            background-color: #ecf0f1;
            padding: 10px;
            margin: 8px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .messages ul li strong {
            color: #2980b9;
        }

        .messages h2 {
            text-align: center;
            color: #2c3e50;
        }

        .user-info {
            text-align: right;
            margin-top: 15px;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f4f8;
            color: #333;
            text-align: center; /* Centering all the text */
        }

        header {
            background-color: #34495e;
            padding: 20px;
            color: #fff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            margin: 0;
            font-size: 2.5rem;
        }

        header nav ul {
            list-style: none;
            padding: 0;
            margin: 20px 0 0;
        }

        header nav ul li {
            display: inline;
            margin-right: 30px;
        }

        header nav ul li a {
            color: #fff;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: bold;
            transition: color 0.3s ease;
        }

        header nav ul li a:hover {
            color: #f39c12;
        }

        .container {
            display: flex;
            justify-content: center; /* Center the container */
            gap: 30px;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Highlight the active link */
        nav ul li a.active {
            background-color: #2980b9; /* Change the background color to highlight */
            color: white; /* Make text white for better contrast */
            font-weight: bold; /* Optional: Make the active link bold */
        }

        h2 {
            font-size: 1.8rem;
            color: #2c3e50;
        }

        .project-info {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 60%; /* Adjusting the width for better centering */
            margin: 0 auto;
            transition: transform 0.3s ease;
        }

        .project-info:hover {
            transform: translateY(-5px);
        }

        .project-info h3 {
            color: #3498db;
            margin-bottom: 10px;
        }

        .project-info ul {
            padding-left: 20px;
            font-size: 1.1rem;
        }

        .project-info ul li {
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .project-info p {
            font-size: 1.1rem;
            line-height: 1.8;
        }

        .user-info {
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>

<body>

    <header>
    <h1 style="color: #ffffff; text-align: center;">SafeHome Dashboard</h1>
    <nav>
        <ul>
            <li><a href="index.php">Home</a></li>
            <li><a href="dashboard.php" class="active">Dashboard</a></li>
            <li><a href="configure.php">Configure Camera</a></li>
            <li><a href="profile.php">Profile</a></li>
        </ul>
    </nav>

    <?php if ($username): ?>
    <div class="user-info" style="text-align: center; margin-top: 20px;">
        <p>Logged in as: <?php echo htmlspecialchars($username); ?></p>
    </div>
    <?php endif; ?>
</header>

    <div class="container">

        <!-- Device List Section -->
        <div class="device-list">
            <h2>Device List</h2>

            <?php if ($userDevices && $deviceLinks): ?>
                <table>
                    <tr>
                        <th>Camera</th>
                        <th>Video Stream</th>
                        <th>Action</th>
                    </tr>

                    <?php foreach ($userDevices as $device): ?>
                        <?php if (isset($device['username']) && $device['username'] === $username): ?>

                            <?php
                                $macAddress = $device['macAddress'];
                                $nickname = null;

                                foreach ($cameraInfo as $camera) {
                                    if ($camera['macAddress'] === $macAddress) {
                                        $nickname = $camera['nickname'];
                                        break;
                                    }
                                }

                                $link = isset($deviceLinks[$macAddress]) ? $deviceLinks[$macAddress] : null;
                            ?>

                            <tr>
                                <td><?php echo htmlspecialchars($nickname ? $nickname : 'No nickname'); ?></td>
                                <td>
                                    <?php if ($link): ?>
                                        <iframe src="<?php echo htmlspecialchars($link); ?>" allow="autoplay"></iframe>
                                    <?php else: ?>
                                        Link not found
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <form method="POST" action="">
                                        <input type="hidden" name="remove_mac" value="<?php echo htmlspecialchars($macAddress); ?>">
                                        <button type="submit" class="remove-button">Remove</button>
                                        <button type="button" class="edit-button" onclick="redirectToEdit('<?php echo htmlspecialchars($macAddress); ?>')">Edit</button>
                                    </form>

                                    <script>
                                        function redirectToEdit(macAddress) {
                                        // Redirect to redirect.php with the MAC address as a query parameter
                                        window.location.href = 'edit_device.php?mac=' + encodeURIComponent(macAddress);
                                        }
                                    </script>
                                </td>
                            </tr>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </table>
            <?php else: ?>
                <p>No devices found.</p>
            <?php endif; ?>
        </div>
<div class="messages">
    <h2>Last Messages</h2>

    <?php if ($results): ?>
    <ul>
        <?php
        // Get all the user devices' MAC addresses
        $userMacAddresses = array_column(array_filter($userDevices, function ($device) use ($username) {
            return isset($device['username']) && $device['username'] === $username;
        }), 'macAddress');

        $messagesWithTimestamp = [];

        // Loop through each result and prepare the messages with their timestamps
        foreach ($results as $key => $message) {
            // Extract the MAC address from the key
            $keyParts = explode('_', $key);
            $macAddress = $keyParts[0];

            // Check if the MAC address is in the user's devices list
            if (in_array($macAddress, $userMacAddresses)) {
                // Check if we have the correct timestamp format (day, month, hour, minute, second)
                if (count($keyParts) >= 6) {
                    $day = $keyParts[1];
                    $month = $keyParts[2];
                    $hour = $keyParts[3];
                    $minute = $keyParts[4];
                    $second = $keyParts[5]; // Extract second field

                    // Create a timestamp from the current year (using a fixed year or dynamic year can be used)
                    $currentYear = date("Y"); // Get the current year
                    $timestamp = mktime($hour, $minute, $second, $month, $day, $currentYear); // Include the current year
                    $readableTimestamp = "$hour:$minute:$second at $day/$month"; // Human-readable format without the year
                } else {
                    $timestamp = 0; // If timestamp format is invalid, assign 0
                    $readableTimestamp = "Invalid Timestamp Format";
                }

                // Get the camera's nickname
                $nickname = null;
                foreach ($cameraInfo as $camera) {
                    if ($camera['macAddress'] === $macAddress) {
                        $nickname = $camera['nickname'];
                        break;
                    }
                }

                $displayName = $nickname ? $nickname : $macAddress;

                // Add the message and timestamp to the array
                $messagesWithTimestamp[] = [
                    'message' => $message,
                    'nickname' => $displayName,
                    'timestamp' => $timestamp,
                    'readableTimestamp' => $readableTimestamp,
                    'macAddress' => $macAddress, // Store macAddress for later use
                    'timestampStr' => "$day-$month-$hour-$minute-$second" // Store timestamp as string for file matching
                ];
            }
        }

        // Sort messages by timestamp (latest first)
        usort($messagesWithTimestamp, function($a, $b) {
            return $b['timestamp'] - $a['timestamp']; // Descending order of timestamp
        });

        // Output the sorted messages (latest first)
        $messageCount = 0;
        foreach ($messagesWithTimestamp as $messageData):
            echo "<li>Camera in <strong>" . htmlspecialchars($messageData['nickname']) . "</strong> detected: ";
            echo htmlspecialchars($messageData['message']) . " (Time: " . $messageData['readableTimestamp'] . ")</li>";

            $messageCount++;
            if ($messageCount >= 5) break; // Show only the last 5 messages
        endforeach;
        ?>
    </ul>
    <?php else: ?>
        <p>No messages available.</p>
    <?php endif; ?>
</div> <!-- End of .messages div -->

<!-- Make sure to close the rest of the HTML tags -->
</body>
</html>
