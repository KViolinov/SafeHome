<?php
session_start();

// Firebase configuration URLs
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json');
define('FIREBASE_DEVICE_LINKS_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json');
define('FIREBASE_MESSAGES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/messages.json');

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

// Remove device link if "remove" action is requested
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['remove_mac'])) {
    $macToRemove = $_POST['remove_mac'];
    $firebaseDeleteUrl = FIREBASE_DEVICE_LINKS_URL . '/' . urlencode($macToRemove) . '.json';
    firebaseRequest($firebaseDeleteUrl, 'DELETE');
    header('Location: ' . $_SERVER['PHP_SELF']);
    exit();
}

// Fetch all user devices, device links, and messages from Firebase
$userDevices = firebaseRequest(FIREBASE_USER_DEVICES_URL);
$deviceLinks = firebaseRequest(FIREBASE_DEVICE_LINKS_URL);
$messages = firebaseRequest(FIREBASE_MESSAGES_URL);

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
        .container {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            padding: 20px;
        }

        .device-list {
            flex: 1;
            max-width: 60%;
        }

        .messages {
            flex: 1;
            max-width: 35%;
            padding: 15px;
            border: 1px solid #ddd;
        }

        .messages h2 {
            text-align: center;
        }

        .messages ul {
            list-style-type: none;
            padding: 0;
        }

        .messages ul li {
            background: #f4f4f4;
            margin: 5px 0;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Device List Section -->
        <div class="device-list">
            <header>
                <h1>Dashboard</h1>
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
                        <th>Action</th>
                    </tr>
                    <?php foreach ($userDevices as $device): ?>
                        <?php if (isset($device['username']) && $device['username'] === $username): ?>
                            <?php 
                                $macAddress = $device['macAddress'];
                                $link = isset($deviceLinks[$macAddress]) ? $deviceLinks[$macAddress] : null;
                            ?>
                            <tr>
                                <td><?php echo htmlspecialchars($macAddress); ?></td>
                                <td>
                                    <?php if ($link): ?>
                                        <iframe src="<?php echo htmlspecialchars($link); ?>" 
                                                style="width: 400px; height: 300px; border: none;" 
                                                allow="autoplay" 
                                                onload="bypassNgrokWarning(this)"></iframe>
                                    <?php else: ?>
                                        Link not found
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <form method="POST" action="">
                                        <input type="hidden" name="remove_mac" value="<?php echo htmlspecialchars($macAddress); ?>">
                                        <button type="submit" class="remove-button">Remove from Dashboard</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </table>
            <?php else: ?>
                <p>No devices found.</p>
            <?php endif; ?>
        </div>

        <!-- Last Messages Section -->
        <div class="messages">
            <h2>Last Messages</h2>
            <?php if ($messages): ?>
                <ul>
                    <?php foreach ($messages as $message): ?>
                        <li><?php echo htmlspecialchars($message); ?></li>
                    <?php endforeach; ?>
                </ul>
            <?php else: ?>
                <p>No messages found.</p>
            <?php endif; ?>
        </div>
    </div>

    <script>
        function bypassNgrokWarning(iframe) {
            iframe.contentWindow.addEventListener("load", function() {
                try {
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
