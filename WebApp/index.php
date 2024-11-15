<?php
session_start();
$username = isset($_SESSION['username']) ? $_SESSION['username'] : null;
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
    </style>
</head>

<body>

    <header>
        <h1>Welcome to SafeHome</h1>
        <nav>
            <ul>
                <li><a href="index.php" class="active">Home</a></li>
                <li><a href="dashboard.php">Dashboard</a></li>
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

    <div class="project-info">
        <h2>Проект: SafeHome</h2>
        <h3>4.1 Цели</h3>
        <p>
            Основната цел на проекта е да създаде цялостна платформа за управление и мониторинг на домашната сигурност, използвайки Machine Learning и AI за анализ на данни и открития на аномалии. Платформата ще използва SafeHome Camera Kit – комплект от камера и сензори, базиран на ESP32, за да следи за движение, нива на температура, въздух и пожарна безопасност.
        </p>

        <h3>4.5 Реализация</h3>
        <ul>
            <li>Камера и сензори – ESP32 с камера модул и допълнителни сензори за температура, качество на въздуха и движение.</li>
            <li>Софтуерни компоненти – Python скриптове и PHP скриптове за обработка на данни и машинно обучение.</li>
            <li>Потребителски интерфейси – уеб и мобилни приложения за визуализация на резултати и управление на устройството.</li>
        </ul>

        <h3>4.3 Ниво на сложност</h3>
        <p>
            Проектът изисква знания по програмиране на микроконтролери (C++ за ESP32), уеб програмиране (HTML, CSS, JavaScript), машинно обучение и IoT интеграция.
        </p>
    </div>

</body>
</html>
