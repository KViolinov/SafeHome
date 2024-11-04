<?php
session_start();

// Firebase configuration URLs
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json');
define('FIREBASE_DEVICE_LINKS_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json');

// Function to handle Firebase requests
function firebaseRequest($url, $method = 'GET', $data = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    if ($method == 'POST' || $method == 'PUT') {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    }
    
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Fetch all user devices and device links from Firebase
$userDevices = firebaseRequest(FIREBASE_USER_DEVICES_URL);
$deviceLinks = firebaseRequest(FIREBASE_DEVICE_LINKS_URL);

// Get the logged-in username
$username = isset($_SESSION['username']) ? $_SESSION['username'] : null;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Profile</h1>
            <nav>
                <ul>
                    <li><a href="index.php">Dashboard</a></li>
                    <li><a href="configure.php">Configure Camera</a></li>
                    <li><a href="profile.php">Profile</a></li>
                </ul>
            </nav>
            <?php if ($username): ?>
                <div class="user-info">
                    <p>Logged in as: <?php echo htmlspecialchars($username); ?></p>
                </div>
            <?php endif; ?>
        </header>

        <h1>Device List</h1>

        <?php if ($userDevices && $deviceLinks): ?>
            <table>
                <tr>
                    <th>MAC Address</th>
                    <th>Video Stream</th>
                </tr>
                <?php foreach ($userDevices as $device): ?>
                    <?php if (isset($device['username']) && $device['username'] === $username): ?>
                        <?php 
                            $macAddress = $device['macAddress'];
                            $link = isset($deviceLinks[$macAddress]) ? $deviceLinks[$macAddress] : null;
                        ?>
                        <?php if ($link): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($macAddress); ?></td>
                                <td>
                                    <iframe src="<?php echo htmlspecialchars($link); ?>" 
                                            style="width: 400px; height: 300px; border: none;" 
                                            allow="autoplay" 
                                            onload="bypassNgrokWarning(this)"></iframe>
                                </td>
                            </tr>
                        <?php else: ?>
                            <tr>
                                <td><?php echo htmlspecialchars($macAddress); ?></td>
                                <td>Link not found</td>
                            </tr>
                        <?php endif; ?>
                    <?php endif; ?>
                <?php endforeach; ?>
            </table>
        <?php else: ?>
            <p>No devices found.</p>
        <?php endif; ?>
    </div>

    <script>
        function bypassNgrokWarning(iframe) {
            iframe.contentWindow.addEventListener("load", function() {
                try {
                    // Check if "Visit Site" button exists in the iframe and click it
                    const visitButton = iframe.contentWindow.document.querySelector("a[href*='ngrok.com']");
                    if (visitButton) {
                        visitButton.click();
                    }
                } catch (e) {
                    console.error("Could not access the iframe content:", e);
                }
            });
        }
    </script>
</body>
</html>
