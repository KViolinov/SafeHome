<?php
session_start();
session_start();

// Firebase configuration
define('FIREBASE_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json');
define('FIREBASE_CAMERA_INFO_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/camera_info.json');
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json');

// Check if username exists in session and assign it
$username = isset($_SESSION['username']) ? $_SESSION['username'] : 'Guest';

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
    addToUserDashboard($username, $macAddress);

    echo "<script>alert('Camera info and Ngrok link saved successfully!');</script>";
}

?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeHome - Home</title>
    <link rel="stylesheet" href="style.css">
    <style>
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
        
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f7fc;
        }
        .container {
            padding: 20px;
        }
        header {
            background-color: #34495e;
            color: white;
            padding: 20px;
            text-align: center;
        }
        header nav ul {
            list-style: none;
            padding: 0;
            text-align: center;
        }
        header nav ul li {
            display: inline;
            margin: 0 15px;
        }
        header nav ul li a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
        .search-container {
            margin: 20px 0;
            text-align: center;
        }
        .search-container input[type="text"] {
            padding: 10px;
            width: 70%;
            font-size: 16px;
            margin-right: 10px;
        }
        .search-container button {
            padding: 10px 15px;
            background-color: #2d2d2d;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        .search-container button:hover {
            background-color: #45a049;
        }
        p {
            color: #ffffff; /* Make text white */
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        form {
            margin-bottom: 10px;
        }
        form input, form select {
            padding: 5px;
            margin: 5px;
        }
        
        nav ul li a.active {
    background-color: #2980b9; /* Change the background color to highlight */
    color: white; /* Make text white for better contrast */
    font-weight: bold; /* Optional: Make the active link bold */
        }
    </style>
</head>

<body>

    <header>
        <h1>Configure Camera</h1>
        <nav>
            <ul>
                <li><a href="index.php">Home</a></li>
                <li><a href="dashboard.php">Dashboard</a></li>
                <li><a href="configure.php" class="active">Configure Camera</a></li>
                <li><a href="profile.php">Profile</a></li>
            </ul>
        </nav>

        <?php if ($username): ?>
<div class="user-info">
    <p>Logged in as: <?php echo htmlspecialchars($username); ?></p>
</div>
<?php endif; ?>

    </header>

    <main>
            <h2>Discovered Device Links</h2>

            <!-- Search form -->
            <div class="search-container">
                <form method="post">
                    <input type="text" name="search_mac" class="form-control" placeholder="Search by MAC Address">
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
            </div>

            <table>
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


</body>
</html>
