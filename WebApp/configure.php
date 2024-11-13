<?php
session_start();
// Firebase configuration
define('FIREBASE_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json'); // Replace with your Firebase URL
define('FIREBASE_CAMERA_INFO_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/camera_info.json'); // Firebase camera info URL
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json'); // Firebase user devices URL

// Function to fetch data from Firebase
function fetchDataFromFirebase() {
    $url = FIREBASE_URL;
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    $json_data = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close($ch);
    return json_decode($json_data, true);
}

// Function to save camera info in Firebase
function saveCameraInfo($cameraData) {
    $url = FIREBASE_CAMERA_INFO_URL;
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($cameraData));
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_exec($ch);
    curl_close($ch);
}

// Function to add a device link (Ngrok link) to the user's dashboard in Firebase
function addToUserDashboard($username, $macAddress) {
    $url = FIREBASE_USER_DEVICES_URL;
    $data = [
        'username' => $username,
        'macAddress' => $macAddress
    ];
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_exec($ch);
    curl_close($ch);
}

// Fetch device links from Firebase
$device_links = fetchDataFromFirebase();

// Search functionality variables (initialize empty)
$search_mac = "";
$filtered_links = [];

// Check if search form submitted
if (isset($_POST['search_mac'])) {
    $search_mac = htmlspecialchars($_POST['search_mac']);
    foreach ($device_links as $mac => $ngrokLink) {
        if (stristr($mac, $search_mac) !== false) {
            $filtered_links[$mac] = $ngrokLink;
        }
    }
}

// Handle "Save Camera Info" action
if (isset($_POST['save_camera_info'])) {
    $cameraData = [
        'username' => $_SESSION['username'],
        'macAddress' => htmlspecialchars($_POST['mac_address']),
        'nickname' => htmlspecialchars($_POST['nickname']),
        'location' => htmlspecialchars($_POST['location']),
        'type' => htmlspecialchars($_POST['type']) // Indoor or Outdoor
    ];
    saveCameraInfo($cameraData);

    // Also add to user dashboard with Ngrok link
    $macAddress = htmlspecialchars($_POST['mac_address']);
    $ngrokLink = $device_links[$macAddress] ?? '';
    $username = $_SESSION['username'];
    addToUserDashboard($username, $macAddress, $ngrokLink);

    echo 'Camera info and Ngrok link saved successfully!';
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configure Camera</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Camera Setup and Configuration</h1>
            <nav>
                <ul>
                    <li><a href="index.php">Dashboard</a></li>
                    <li><a href="configure.php">Configure Camera</a></li>
                    <li><a href="profile.php">Profile</a></li>
                </ul>
            </nav>
            <?php if (isset($_SESSION['username'])): ?>
                <div class="user-info">
                    <p>Logged in as: <?php echo $_SESSION['username']; ?></p>
                </div>
            <?php endif; ?>
        </header>

        <main>
            <h2>Discovered Device Links</h2>

            <!-- Search form -->
            <form method="post" class="mb-3 d-flex" style="max-width: 400px; margin-bottom: 20px;">
                <input type="text" name="search_mac" class="form-control" placeholder="Search by MAC Address" style="flex: 1;">
                <button type="submit" class="btn btn-primary ml-2">Search</button>
            </form>

            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>MAC Address</th>
                        <th>Link</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (!empty($filtered_links)): ?>
                        <?php foreach ($filtered_links as $mac => $ngrokLink): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($mac); ?></td>
                                <td><a href="<?php echo htmlspecialchars($ngrokLink); ?>" target="_blank"><?php echo htmlspecialchars($ngrokLink); ?></a></td>
                                <td>
                                    <!-- Form to capture additional camera info -->
                                    <form method="post">
                                        <input type="hidden" name="mac_address" value="<?php echo htmlspecialchars($mac); ?>">
                                        <label>Nickname: <input type="text" name="nickname" required></label>
                                        <label>Location: <input type="text" name="location" required></label>
                                        <label>Type:
                                            <select name="type" required>
                                                <option value="Indoor">Indoor</option>
                                                <option value="Outdoor">Outdoor</option>
                                            </select>
                                        </label>
                                        <button type="submit" name="save_camera_info" class="btn btn-success">Save Camera Info</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php elseif (isset($_POST['search_mac']) && empty($filtered_links)): ?>
                        <tr>
                            <td colspan="3">No devices found for "<?php echo htmlspecialchars($search_mac); ?>".</td>
                        </tr>
                    <?php else: ?>
                        <tr>
                            <td colspan="3">No devices found.</td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
