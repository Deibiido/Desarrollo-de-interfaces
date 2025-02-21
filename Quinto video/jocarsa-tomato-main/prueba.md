# Estructura del Proyecto

- **🗀  jocarsa-tomato-main/**
    - 🗋  index.php
    - 🗋  manual.py
    - 🗋  prueba.md
    - 🗋  README.md
    - 🗋  tomato.py
    - **🗀  datos/**
        - 🗋  carga_300sec.txt
        - 🗋  carga_60min.txt
        - 🗋  carga_historical.txt
        - **🗀  historical/**
            - 🗋  carga_historical.txt
            - 🗋  conexiones_activas_historical.jpg
            - 🗋  descarga_historical.jpg
            - 🗋  subida_historical.jpg
            - 🗋  temperatura_historical.jpg
            - 🗋  uso_de_cpu_historical.jpg
            - 🗋  uso_de_disco_historical.jpg
            - 🗋  uso_de_ram_historical.jpg
        - **🗀  min5/**
            - 🗋  carga_300sec.txt
            - 🗋  conexiones_activas_300sec.jpg
            - 🗋  descarga_300sec.jpg
            - 🗋  subida_300sec.jpg
            - 🗋  temperatura_300sec.jpg
            - 🗋  uso_de_cpu_300sec.jpg
            - 🗋  uso_de_disco_300sec.jpg
            - 🗋  uso_de_ram_300sec.jpg
        - **🗀  min60/**
            - 🗋  carga_60min.txt
            - 🗋  conexiones_activas_60min.jpg
            - 🗋  descarga_60min.jpg
            - 🗋  subida_60min.jpg
            - 🗋  temperatura_60min.jpg
            - 🗋  uso_de_cpu_60min.jpg
            - 🗋  uso_de_disco_60min.jpg
            - 🗋  uso_de_ram_60min.jpg

# Documentación de Archivos

## index.php

Start the session at the beginning of the script


# Código de Archivos

## index.php

```php
<?php
// Start the session at the beginning of the script
session_start();

// Define valid credentials
$VALID_USERNAME = 'jocarsa';
$VALID_PASSWORD = 'jocarsa';

// Handle Logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    // Destroy the session
    session_unset();
    session_destroy();
    // Redirect to the login form
    header("Location: index.php");
    exit;
}

// Handle Login Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? trim($_POST['password']) : '';
    if ($username === $VALID_USERNAME && $password === $VALID_PASSWORD) {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $username;
        header("Location: index.php");
        exit;
    } else {
        $error = "Usuario o contraseña inválidos.";
    }
}

$loggedIn = isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true;

// =====================
// Función para obtener imágenes de una carpeta
// =====================
function getImages($folder) {
    $images = [];
    if (is_dir($folder)) {
        $files = scandir($folder);
        foreach ($files as $file) {
            if (preg_match('/\.(jpg|jpeg|png|gif|svg)$/i', $file)) {
                $images[] = $file;
            }
        }
    }
    return $images;
}

// =====================
// Función para extraer el "prefijo" de la métrica a partir del nombre del archivo
// Ejemplo: "uso_de_cpu_historical.jpg" => "uso_de_cpu"
// =====================
function getMetricPrefix($filename) {
    // Elimina la parte final: "_historical.jpg", "_60min.jpg" o "_300sec.jpg"
    // Esto deja únicamente "uso_de_cpu", "uso_de_ram", etc.
    return preg_replace('/_\w+\.jpg$/', '', $filename);
}

// =====================
// Directorios donde tu script Python genera imágenes
// =====================
$chartFolders = [
    'historical' => 'datos/historical',
    '60min'      => 'datos/min60',
    '300sec'     => 'datos/min5',
];

// Tomar el tipo de gráfica seleccionado, por defecto "historical"
$selectedType = isset($_GET['type']) && isset($chartFolders[$_GET['type']]) ? $_GET['type'] : 'historical';

// Si el usuario está logueado, obtener la lista de imágenes en la carpeta elegida
$images = $loggedIn ? getImages($chartFolders[$selectedType]) : [];
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>jocarsa | Tomato</title>
  <link rel="icon" href="https://jocarsa.com/static/logo/tomato.png" type="image/svg+xml">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap');

    /* Reset y estilos generales */
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: Ubuntu, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f2f5;
      color: #333;
      min-height: 100vh;
    }

    /* Header */
    .header {
      background-color: tomato;
      width: 100%;
      padding: 15px 30px;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: fixed;
      top: 0;
      left: 0;
      z-index: 100;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header .app-name {
      font-size: 1.5rem;
      font-weight: bold;
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      justify-content: center;
      align-items: center;
      align-content: stretch;
    }
    .header .app-name img {
      width: 50px;
      margin-right: 20px;
    }
    .header .logout-button {
      background-color: tomato;
      color: white;
      border: 2px solid white;
      padding: 8px 16px;
      border-radius: 25px;
      cursor: pointer;
      text-decoration: none;
      font-size: 1rem;
      transition: background-color 0.3s, border-color 0.3s;
    }
    .header .logout-button:hover {
      background-color: darkred;
      border-color: darkred;
    }

    /* Sidebar */
    .sidebar {
      width: 250px;
      background: #fff;
      padding: 20px;
      border-right: 1px solid #ddd;
      position: fixed;
      top: 70px; /* altura del header */
      bottom: 0;
      overflow-y: auto;
      box-shadow: 2px 0 5px rgba(0,0,0,0.05);
    }
    .sidebar h3 {
      margin-bottom: 20px;
      color: tomato;
      font-size: 1.2rem;
    }
    .sidebar a {
      display: block;
      padding: 12px 16px;
      margin: 8px 0;
      color: tomato;
      text-decoration: none;
      border-radius: 8px;
      transition: background-color 0.3s, color 0.3s;
    }
    .sidebar a:hover,
    .sidebar a.active {
      background-color: tomato;
      color: white;
    }

    /* Content */
    .content {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      margin-top: 70px; /* altura del header */
      margin-left: 270px; /* ancho de la sidebar + margen */
    }

    /* Barra de filtros (checkboxes) */
    .filters {
      margin-bottom: 20px;
      background: #fff;
      padding: 10px 15px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .filters label {
      margin-right: 15px;
      cursor: pointer;
    }

    .dashboard {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }
    .image-card {
      text-align: center;
      background: #fff;
      padding: 15px;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .image-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .image-card img {
      max-width: 100%;
      height: auto;
      border-radius: 10px;
    }

    /* Modal */
    .modal {
      display: none;
      position: fixed;
      z-index: 200;
      padding-top: 60px;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      overflow: auto;
      background-color: rgba(0,0,0,0.8);
    }
    .modal-content {
      margin: auto;
      display: block;
      max-width: 90%;
      max-height: 80%;
      border-radius: 10px;
      animation-name: zoom;
      animation-duration: 0.6s;
    }
    @keyframes zoom {
      from {transform:scale(0)}
      to {transform:scale(1)}
    }
    .close {
      position: absolute;
      top: 30px;
      right: 35px;
      color: #f1f1f1;
      font-size: 40px;
      font-weight: bold;
      transition: color 0.3s;
      cursor: pointer;
    }
    .close:hover,
    .close:focus {
      color: #bbb;
      text-decoration: none;
      cursor: pointer;
    }

    /* Login */
    .login-container {
      background: #fff;
      padding: 40px 30px;
      max-width: 400px;
      width: 90%;
      margin: 100px auto;
      border-radius: 10px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.1);
      text-align: center;
      position: relative;
    }
    .login-container .logo {
      width: 100px;
      margin-bottom: 20px;
    }
    .login-container h2 {
      margin-bottom: 20px;
      color: tomato;
      font-size: 1.8rem;
    }
    .login-container .error {
      background-color: #f8d7da;
      color: #842029;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.95rem;
    }
    .login-container label {
      display: block;
      margin-bottom: 5px;
      text-align: left;
      color: #555;
      font-size: 0.95rem;
    }
    .login-container input {
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 20px;
      border: 1px solid #ddd;
      border-radius: 5px;
      font-size: 1rem;
      transition: border-color 0.3s;
    }
    .login-container input:focus {
      border-color: tomato;
      outline: none;
    }
    .login-container button {
      width: 100%;
      padding: 12px;
      background-color: tomato;
      border: none;
      color: white;
      font-size: 1rem;
      border-radius: 25px;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    .login-container button:hover {
      background-color: darkred;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar {
        width: 200px;
      }
      .content {
        margin-left: 220px;
      }
    }
    @media (max-width: 576px) {
      .sidebar {
        display: none;
      }
      .content {
        margin-left: 0;
      }
      .header {
        flex-direction: column;
        align-items: flex-start;
      }
      .header .logout-button {
        margin-top: 10px;
      }
    }
  </style>
</head>
<body>
<?php if ($loggedIn): ?>
    <!-- Header -->
    <div class="header">
      <div class="app-name">
        <img src="https://jocarsa.com/static/logo/tomato.png" alt="Logo">
        jocarsa | Tomato
      </div>
      <a href="index.php?action=logout" class="logout-button">Cerrar Sesión</a>
    </div>

    <!-- Sidebar -->
    <div class="sidebar">
      <h3>Gráficas</h3>
      <a href="index.php?type=historical" class="<?php echo $selectedType === 'historical' ? 'active' : ''; ?>">Histórico</a>
      <a href="index.php?type=60min" class="<?php echo $selectedType === '60min' ? 'active' : ''; ?>">Última Hora</a>
      <a href="index.php?type=300sec" class="<?php echo $selectedType === '300sec' ? 'active' : ''; ?>">Últimos 5 Minutos</a>
    </div>

    <!-- Main Content -->
    <div class="content">
      <!-- Barra de filtros: checkboxes para cada métrica -->
      <div class="filters">
        <label><input type="checkbox" name="filter" value="uso_de_cpu" checked> CPU</label>
        <label><input type="checkbox" name="filter" value="uso_de_ram" checked> RAM</label>
        <label><input type="checkbox" name="filter" value="uso_de_disco" checked> Disco</label>
        <label><input type="checkbox" name="filter" value="descarga" checked> Descarga</label>
        <label><input type="checkbox" name="filter" value="subida" checked> Subida</label>
        <label><input type="checkbox" name="filter" value="temperatura" checked> Temperatura</label>
        <label><input type="checkbox" name="filter" value="conexiones_activas" checked> Conexiones</label>
      </div>

      <div class="dashboard">
        <?php if (!empty($images)): ?>
            <?php foreach ($images as $image): ?>
                <?php 
                  // Extraer el "prefijo" de la métrica (ej. "uso_de_cpu") para usarlo en data-metric
                  $metricPrefix = getMetricPrefix($image);
                ?>
                <div class="image-card" data-metric="<?php echo $metricPrefix; ?>"
                     onclick="openModal('<?php echo htmlspecialchars($chartFolders[$selectedType] . '/' . $image); ?>')">
                  <img src="<?php echo htmlspecialchars($chartFolders[$selectedType] . '/' . $image); ?>" alt="Chart">
                </div>
            <?php endforeach; ?>
        <?php else: ?>
            <p>No hay gráficas disponibles en la carpeta seleccionada.</p>
        <?php endif; ?>
      </div>
    </div>

    <!-- The Modal -->
    <div id="myModal" class="modal">
      <span class="close" onclick="closeModal()">&times;</span>
      <img class="modal-content" id="modalImage" alt="Chart Enlarged">
    </div>

    <!-- JavaScript para Modal y Filtrado -->
    <script>
      function openModal(src) {
        var modal = document.getElementById("myModal");
        var modalImg = document.getElementById("modalImage");
        modal.style.display = "block";
        modalImg.src = src;
      }

      function closeModal() {
        var modal = document.getElementById("myModal");
        modal.style.display = "none";
      }

      // Cerrar modal al hacer click fuera de la imagen
      window.onclick = function(event) {
        var modal = document.getElementById("myModal");
        if (event.target == modal) {
          modal.style.display = "none";
        }
      }

      // Escuchar cambios en los checkboxes y mostrar/ocultar gráficas
      const checkboxes = document.querySelectorAll('.filters input[type="checkbox"]');
      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', function() {
          const metric = this.value; // ej. "uso_de_cpu"
          const isChecked = this.checked;
          // Seleccionar todas las image-card con data-metric="uso_de_cpu"
          document.querySelectorAll('.image-card[data-metric="'+metric+'"]').forEach((card) => {
            card.style.display = isChecked ? 'block' : 'none';
          });
        });
      });
    </script>
<?php else: ?>
    <!-- Login Form -->
    <div class="login-container">
      <img src="https://jocarsa.com/static/logo/tomato.png" alt="Tomato Logo" class="logo">
      <h2>Iniciar Sesión</h2>
      <?php if (isset($error)): ?>
          <div class="error"><?php echo htmlspecialchars($error); ?></div>
      <?php endif; ?>
      <form action="index.php" method="post">
        <label for="username">Usuario</label>
        <input type="text" id="username" name="username" required placeholder="Ingresa tu usuario">
        <label for="password">Contraseña</label>
        <input type="password" id="password" name="password" required placeholder="Ingresa tu contraseña">
        <button type="submit" name="login">Entrar</button>
      </form>
    </div>
<?php endif; ?>
</body>
</html>

```

## manual.py

```python
import subprocess
import time

def main():
    script_path = "tomato.py"  # Replace with the actual path to your script
    try:
        while True:
            subprocess.run(["python3", script_path], check=True)  # Adjust 'python' if necessary (e.g., 'python3')
            time.sleep(1)  # Optional delay between iterations
    except KeyboardInterrupt:
        print("Loop stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Script execution failed: {e}")

if __name__ == "__main__":
    main()

```

## prueba.md

```
# Estructura del Proyecto

- **🗀  jocarsa-tomato-main/**
    - 🗋  index.php
    - 🗋  manual.py
    - 🗋  prueba.md
    - 🗋  README.md
    - 🗋  tomato.py
    - **🗀  datos/**
        - 🗋  carga_300sec.txt
        - 🗋  carga_60min.txt
        - 🗋  carga_historical.txt
        - **🗀  historical/**
            - 🗋  carga_historical.txt
            - 🗋  conexiones_activas_historical.jpg
            - 🗋  descarga_historical.jpg
            - 🗋  subida_historical.jpg
            - 🗋  temperatura_historical.jpg
            - 🗋  uso_de_cpu_historical.jpg
            - 🗋  uso_de_disco_historical.jpg
            - 🗋  uso_de_ram_historical.jpg
        - **🗀  min5/**
            - 🗋  carga_300sec.txt
            - 🗋  conexiones_activas_300sec.jpg
            - 🗋  descarga_300sec.jpg
            - 🗋  subida_300sec.jpg
            - 🗋  temperatura_300sec.jpg
            - 🗋  uso_de_cpu_300sec.jpg
            - 🗋  uso_de_disco_300sec.jpg
            - 🗋  uso_de_ram_300sec.jpg
        - **🗀  min60/**
            - 🗋  carga_60min.txt
            - 🗋  conexiones_activas_60min.jpg
            - 🗋  descarga_60min.jpg
            - 🗋  subida_60min.jpg
            - 🗋  temperatura_60min.jpg
            - 🗋  uso_de_cpu_60min.jpg
            - 🗋  uso_de_disco_60min.jpg
            - 🗋  uso_de_ram_60min.jpg

# Documentación de Archivos

## index.php

Start the session at the beginning of the script


# Código de Archivos

## index.php

```php
<?php
// Start the session at the beginning of the script
session_start();

// Define valid credentials
$VALID_USERNAME = 'jocarsa';
$VALID_PASSWORD = 'jocarsa';

// Handle Logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    // Destroy the session
    session_unset();
    session_destroy();
    // Redirect to the login form
    header("Location: index.php");
    exit;
}

// Handle Login Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? trim($_POST['password']) : '';
    if ($username === $VALID_USERNAME && $password === $VALID_PASSWORD) {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $username;
        header("Location: index.php");
        exit;
    } else {
        $error = "Usuario o contraseña inválidos.";
    }
}

$loggedIn = isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true;

// =====================
// Función para obtener imágenes de una carpeta
// =====================
function getImages($folder) {
    $images = [];
    if (is_dir($folder)) {
        $files = scandir($folder);
        foreach ($files as $file) {
            if (preg_match('/\.(jpg|jpeg|png|gif|svg)$/i', $file)) {
                $images[] = $file;
            }
        }
    }
    return $images;
}

// =====================
// Función para extraer el "prefijo" de la métrica a partir del nombre del archivo
// Ejemplo: "uso_de_cpu_historical.jpg" => "uso_de_cpu"
// =====================
function getMetricPrefix($filename) {
    // Elimina la parte final: "_historical.jpg", "_60min.jpg" o "_300sec.jpg"
    // Esto deja únicamente "uso_de_cpu", "uso_de_ram", etc.
    return preg_replace('/_\w+\.jpg$/', '', $filename);
}

// =====================
// Directorios donde tu script Python genera imágenes
// =====================
$chartFolders = [
    'historical' => 'datos/historical',
    '60min'      => 'datos/min60',
    '300sec'     => 'datos/min5',
];

// Tomar el tipo de gráfica seleccionado, por defecto "historical"
$selectedType = isset($_GET['type']) && isset($chartFolders[$_GET['type']]) ? $_GET['type'] : 'historical';

// Si el usuario está logueado, obtener la lista de imágenes en la carpeta elegida
$images = $loggedIn ? getImages($chartFolders[$selectedType]) : [];
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>jocarsa | Tomato</title>
  <link rel="icon" href="https://jocarsa.com/static/logo/tomato.png" type="image/svg+xml">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap');

    /* Reset y estilos generales */
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: Ubuntu, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f2f5;
      color: #333;
      min-height: 100vh;
    }

    /* Header */
    .header {
      background-color: tomato;
      width: 100%;
      padding: 15px 30px;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: fixed;
      top: 0;
      left: 0;
      z-index: 100;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header .app-name {
      font-size: 1.5rem;
      font-weight: bold;
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      justify-content: center;
      align-items: center;
      align-content: stretch;
    }
    .header .app-name img {
      width: 50px;
      margin-right: 20px;
    }
    .header .logout-button {
      background-color: tomato;
      color: white;
      border: 2px solid white;
      padding: 8px 16px;
      border-radius: 25px;
      cursor: pointer;
      text-decoration: none;
      font-size: 1rem;
      transition: background-color 0.3s, border-color 0.3s;
    }
    .header .logout-button:hover {
      background-color: darkred;
      border-color: darkred;
    }

    /* Sidebar */
    .sidebar {
      width: 250px;
      background: #fff;
      padding: 20px;
      border-right: 1px solid #ddd;
      position: fixed;
      top: 70px; /* altura del header */
      bottom: 0;
      overflow-y: auto;
      box-shadow: 2px 0 5px rgba(0,0,0,0.05);
    }
    .sidebar h3 {
      margin-bottom: 20px;
      color: tomato;
      font-size: 1.2rem;
    }
    .sidebar a {
      display: block;
      padding: 12px 16px;
      margin: 8px 0;
      color: tomato;
      text-decoration: none;
      border-radius: 8px;
      transition: background-color 0.3s, color 0.3s;
    }
    .sidebar a:hover,
    .sidebar a.active {
      background-color: tomato;
      color: white;
    }

    /* Content */
    .content {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      margin-top: 70px; /* altura del header */
      margin-left: 270px; /* ancho de la sidebar + margen */
    }

    /* Barra de filtros (checkboxes) */
    .filters {
      margin-bottom: 20px;
      background: #fff;
      padding: 10px 15px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .filters label {
      margin-right: 15px;
      cursor: pointer;
    }

    .dashboard {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }
    .image-card {
      text-align: center;
      background: #fff;
      padding: 15px;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .image-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .image-card img {
      max-width: 100%;
      height: auto;
      border-radius: 10px;
    }

    /* Modal */
    .modal {
      display: none;
      position: fixed;
      z-index: 200;
      padding-top: 60px;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      overflow: auto;
      background-color: rgba(0,0,0,0.8);
    }
    .modal-content {
      margin: auto;
      display: block;
      max-width: 90%;
      max-height: 80%;
      border-radius: 10px;
      animation-name: zoom;
      animation-duration: 0.6s;
    }
    @keyframes zoom {
      from {transform:scale(0)}
      to {transform:scale(1)}
    }
    .close {
      position: absolute;
      top: 30px;
      right: 35px;
      color: #f1f1f1;
      font-size: 40px;
      font-weight: bold;
      transition: color 0.3s;
      cursor: pointer;
    }
    .close:hover,
    .close:focus {
      color: #bbb;
      text-decoration: none;
      cursor: pointer;
    }

    /* Login */
    .login-container {
      background: #fff;
      padding: 40px 30px;
      max-width: 400px;
      width: 90%;
      margin: 100px auto;
      border-radius: 10px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.1);
      text-align: center;
      position: relative;
    }
    .login-container .logo {
      width: 100px;
      margin-bottom: 20px;
    }
    .login-container h2 {
      margin-bottom: 20px;
      color: tomato;
      font-size: 1.8rem;
    }
    .login-container .error {
      background-color: #f8d7da;
      color: #842029;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.95rem;
    }
    .login-container label {
      display: block;
      margin-bottom: 5px;
      text-align: left;
      color: #555;
      font-size: 0.95rem;
    }
    .login-container input {
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 20px;
      border: 1px solid #ddd;
      border-radius: 5px;
      font-size: 1rem;
      transition: border-color 0.3s;
    }
    .login-container input:focus {
      border-color: tomato;
      outline: none;
    }
    .login-container button {
      width: 100%;
      padding: 12px;
      background-color: tomato;
      border: none;
      color: white;
      font-size: 1rem;
      border-radius: 25px;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    .login-container button:hover {
      background-color: darkred;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar {
        width: 200px;
      }
      .content {
        margin-left: 220px;
      }
    }
    @media (max-width: 576px) {
      .sidebar {
        display: none;
      }
      .content {
        margin-left: 0;
      }
      .header {
        flex-direction: column;
        align-items: flex-start;
      }
      .header .logout-button {
        margin-top: 10px;
      }
    }
  </style>
</head>
<body>
<?php if ($loggedIn): ?>
    <!-- Header -->
    <div class="header">
      <div class="app-name">
        <img src="https://jocarsa.com/static/logo/tomato.png" alt="Logo">
        jocarsa | Tomato
      </div>
      <a href="index.php?action=logout" class="logout-button">Cerrar Sesión</a>
    </div>

    <!-- Sidebar -->
    <div class="sidebar">
      <h3>Gráficas</h3>
      <a href="index.php?type=historical" class="<?php echo $selectedType === 'historical' ? 'active' : ''; ?>">Histórico</a>
      <a href="index.php?type=60min" class="<?php echo $selectedType === '60min' ? 'active' : ''; ?>">Última Hora</a>
      <a href="index.php?type=300sec" class="<?php echo $selectedType === '300sec' ? 'active' : ''; ?>">Últimos 5 Minutos</a>
    </div>

    <!-- Main Content -->
    <div class="content">
      <!-- Barra de filtros: checkboxes para cada métrica -->
      <div class="filters">
        <label><input type="checkbox" name="filter" value="uso_de_cpu" checked> CPU</label>
        <label><input type="checkbox" name="filter" value="uso_de_ram" checked> RAM</label>
        <label><input type="checkbox" name="filter" value="uso_de_disco" checked> Disco</label>
        <label><input type="checkbox" name="filter" value="descarga" checked> Descarga</label>
        <label><input type="checkbox" name="filter" value="subida" checked> Subida</label>
        <label><input type="checkbox" name="filter" value="temperatura" checked> Temperatura</label>
        <label><input type="checkbox" name="filter" value="conexiones_activas" checked> Conexiones</label>
      </div>

      <div class="dashboard">
        <?php if (!empty($images)): ?>
            <?php foreach ($images as $image): ?>
                <?php 
                  // Extraer el "prefijo" de la métrica (ej. "uso_de_cpu") para usarlo en data-metric
                  $metricPrefix = getMetricPrefix($image);
                ?>
                <div class="image-card" data-metric="<?php echo $metricPrefix; ?>"
                     onclick="openModal('<?php echo htmlspecialchars($chartFolders[$selectedType] . '/' . $image); ?>')">
                  <img src="<?php echo htmlspecialchars($chartFolders[$selectedType] . '/' . $image); ?>" alt="Chart">
                </div>
            <?php endforeach; ?>
        <?php else: ?>
            <p>No hay gráficas disponibles en la carpeta seleccionada.</p>
        <?php endif; ?>
      </div>
    </div>

    <!-- The Modal -->
    <div id="myModal" class="modal">
      <span class="close" onclick="closeModal()">&times;</span>
      <img class="modal-content" id="modalImage" alt="Chart Enlarged">
    </div>

    <!-- JavaScript para Modal y Filtrado -->
    <script>
      function openModal(src) {
        var modal = document.getElementById("myModal");
        var modalImg = document.getElementById("modalImage");
        modal.style.display = "block";
        modalImg.src = src;
      }

      function closeModal() {
        var modal = document.getElementById("myModal");
        modal.style.display = "none";
      }

      // Cerrar modal al hacer click fuera de la imagen
      window.onclick = function(event) {
        var modal = document.getElementById("myModal");
        if (event.target == modal) {
          modal.style.display = "none";
        }
      }

      // Escuchar cambios en los checkboxes y mostrar/ocultar gráficas
      const checkboxes = document.querySelectorAll('.filters input[type="checkbox"]');
      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', function() {
          const metric = this.value; // ej. "uso_de_cpu"
          const isChecked = this.checked;
          // Seleccionar todas las image-card con data-metric="uso_de_cpu"
          document.querySelectorAll('.image-card[data-metric="'+metric+'"]').forEach((card) => {
            card.style.display = isChecked ? 'block' : 'none';
          });
        });
      });
    </script>
<?php else: ?>
    <!-- Login Form -->
    <div class="login-container">
      <img src="https://jocarsa.com/static/logo/tomato.png" alt="Tomato Logo" class="logo">
      <h2>Iniciar Sesión</h2>
      <?php if (isset($error)): ?>
          <div class="error"><?php echo htmlspecialchars($error); ?></div>
      <?php endif; ?>
      <form action="index.php" method="post">
        <label for="username">Usuario</label>
        <input type="text" id="username" name="username" required placeholder="Ingresa tu usuario">
        <label for="password">Contraseña</label>
        <input type="password" id="password" name="password" required placeholder="Ingresa tu contraseña">
        <button type="submit" name="login">Entrar</button>
      </form>
    </div>
<?php endif; ?>
</body>
</html>


```

## README.md

```
# jocarsa-tomato
```

## tomato.py

```python
import matplotlib.pyplot as plt
import psutil
import time
import subprocess
import os
from datetime import datetime

# Define file paths for each dataset (use raw strings for Windows paths)
data_paths = {
    "historical": "datos/carga_historical.txt",
    "60min":       "datos/carga_60min.txt",
    "300sec":      "datos/carga_300sec.txt",
}

# Define corresponding plot folders
# Define corresponding plot folders as directories
plot_folders = {
    "historical": "datos/historical",
    "60min":       "datos/min60",
    "300sec":      "datos/min5",

}

# Create the plot folders if they don't exist
for folder in plot_folders.values():
    os.makedirs(folder, exist_ok=True)

# Function to trim data based on a time window (in seconds)
def trim_data(data, time_window_seconds):
    now = datetime.now()
    return [entry for entry in data if (now - entry[0]).total_seconds() <= time_window_seconds]

# Load existing data from a file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return [
                (datetime.fromisoformat(row[0]), *map(float, row[1:]))
                for row in (line.strip().split(',') for line in f if line.strip())
            ]
    except FileNotFoundError:
        return []

# Save data to a file
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        for row in data:
            f.write(','.join(map(str, [row[0].isoformat()] + list(row[1:]))) + '\n')

# Measure system metrics
def measure_metrics():
    carga_cpu = psutil.cpu_percent(interval=1)
    carga_ram = psutil.virtual_memory().percent
    uso_disco = psutil.disk_usage('/').percent
    data_inicio = psutil.net_io_counters()
    time.sleep(1)
    data_final = psutil.net_io_counters()
    descarga_mbps = (data_final.bytes_recv - data_inicio.bytes_recv) / (1024 * 1024)
    subida_mbps = (data_final.bytes_sent - data_inicio.bytes_sent) / (1024 * 1024)
    num_conexiones = len(psutil.net_connections())
    temperaturas = list(obtener_temperaturas())
    temperatura_promedio = sum(temperaturas) / len(temperaturas) if temperaturas else 0
    return (
        datetime.now(),
        carga_cpu,
        carga_ram,
        uso_disco,
        descarga_mbps,
        subida_mbps,
        temperatura_promedio,
        num_conexiones,
    )

# Function to obtain CPU temperatures (requires lm-sensors; not implemented here)
def obtener_temperaturas():
    # Uncomment and implement if lm-sensors is available
    # try:
    #     sensores = subprocess.check_output(['sensors'], encoding='utf-8')
    #     for linea in sensores.splitlines():
    #         if 'Core' in linea:
    #             yield float(linea.split()[1].strip('+').strip('°C'))
    # except Exception as e:
    #     print(f"Error al obtener temperaturas: {e}")
    #     return []
    return []

# Load current data for each dataset
data_buffers = {key: load_data(path) for key, path in data_paths.items()}

# Measure new metrics and create a new data entry
new_entry = measure_metrics()

# Update all datasets with the new entry:
# - Historical: keep every entry (full history)
# - 60min: add new entry then trim to last 3600 seconds (60 minutes)
# - 300sec: add new entry then trim to last 300 seconds (5 minutes)
data_buffers["historical"].append(new_entry)
data_buffers["60min"].append(new_entry)
data_buffers["300sec"].append(new_entry)

data_buffers["60min"] = trim_data(data_buffers["60min"], 3600)
data_buffers["300sec"] = trim_data(data_buffers["300sec"], 300)

# Save updated data back to files
for key, path in data_paths.items():
    save_data(path, data_buffers[key])

# Function to generate plots for a given dataset
def generate_plot(data, index, title, ylabel, save_path, ylim=None):
    if not data:
        print(f"No data available for {title}. Skipping plot.")
        return
    timestamps = [row[0] for row in data]
    values = [row[index] for row in data]
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, values, label=title, marker='o')
    plt.grid(True)
    if ylim:
        plt.ylim(ylim)
    plt.title(title)
    plt.xlabel('Tiempo')
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

# Define plot configurations: (data column index, metric title, Y-axis label, optional y-limits)
plot_configs = [
    (1, 'Uso de CPU', 'Porcentaje de Uso', (0, 100)),
    (2, 'Uso de RAM', 'Porcentaje de Uso', (0, 100)),
    (3, 'Uso de Disco', 'Porcentaje de Uso', (0, 100)),
    (4, 'Descarga', 'Mbps', None),
    (5, 'Subida', 'Mbps', None),
    (6, 'Temperatura', 'Temperatura (°C)', None),
    (7, 'Conexiones Activas', 'Conexiones', None),
]

# Generate plots for each dataset (historical, 60min, 300sec)
for dataset_key, data in data_buffers.items():
    for index, title, ylabel, ylim in plot_configs:
        # Build a unique file name per dataset and metric
        save_path = os.path.join(
            plot_folders[dataset_key],
            f'{title.lower().replace(" ", "_")}_{dataset_key}.jpg'
        )
        generate_plot(data, index, f'{title} ({dataset_key})', ylabel, save_path, ylim)

print("Métricas actualizadas y gráficas generadas correctamente.")

```

## datos\carga_300sec.txt

```
2025-02-21T11:45:40.066589,7.8,43.5,90.4,0.01146697998046875,0.026009559631347656,0.0,173.0
2025-02-21T11:46:06.798195,3.9,43.4,90.4,0.000492095947265625,0.0004024505615234375,0,160

```

## datos\carga_60min.txt

```
2025-02-21T11:45:40.066589,7.8,43.5,90.4,0.01146697998046875,0.026009559631347656,0.0,173.0
2025-02-21T11:46:06.798195,3.9,43.4,90.4,0.000492095947265625,0.0004024505615234375,0,160

```

## datos\carga_historical.txt

```
2025-02-21T10:37:39.737331,1.7,44.1,90.2,0.00022411346435546875,5.14984130859375e-05,0.0,165.0
2025-02-21T11:45:40.066589,7.8,43.5,90.4,0.01146697998046875,0.026009559631347656,0.0,173.0
2025-02-21T11:46:06.798195,3.9,43.4,90.4,0.000492095947265625,0.0004024505615234375,0,160

```

## datos\historical\carga_historical.txt

```
2025-02-21T14:55:10,12.3,55.1,70.0,0.12,0.08,50.0,120
2025-02-21T14:57:15,14.7,57.3,71.2,0.14,0.09,50.5,125
2025-02-21T15:00:22,13.9,56.8,70.5,0.13,0.07,50.2,123
2025-02-21T15:02:30,15.1,58.0,71.5,0.15,0.10,50.7,127

```

## datos\min5\carga_300sec.txt

```
2025-02-21T15:00:22,13.9,56.8,70.5,0.13,0.07,50.2,123
2025-02-21T15:02:30,15.1,58.0,71.5,0.15,0.10,50.7,127

```

## datos\min60\carga_60min.txt

```
2025-02-21T14:57:15,14.7,57.3,71.2,0.14,0.09,50.5,125
2025-02-21T15:00:22,13.9,56.8,70.5,0.13,0.07,50.2,123
2025-02-21T15:02:30,15.1,58.0,71.5,0.15,0.10,50.7,127

```


# Anotaciones

Este software se utiliza en servidor
