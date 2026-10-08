\# EV SERVICE – Frontend Flutter



\## Descripción del proyecto



EV SERVICE es una aplicación multiplataforma desarrollada con Flutter y Dart para gestionar servicios de mantenimiento de vehículos eléctricos.



El sistema permite que los clientes registren sus vehículos, programen citas y consulten información sobre los servicios realizados. También incorpora funciones destinadas a la gestión de mantenimiento por parte del personal mecánico.



Este proyecto forma parte de una solución académica que integra una aplicación Flutter, un servidor Flask y una base de datos MariaDB.



\## Funcionalidades principales



\- Registro e inicio de sesión de usuarios.

\- Acceso según el rol de cliente o mecánico.

\- Registro y consulta de vehículos eléctricos.

\- Programación de citas de mantenimiento.

\- Consulta y gestión de citas.

\- Registro de diagnósticos y servicios realizados.

\- Consulta del historial de mantenimiento.

\- Gestión de información relacionada con baterías.

\- Funcionalidades de códigos QR.

\- Generación de reportes en PDF.



\## Tecnologías utilizadas



\- Flutter

\- Dart

\- Python y Flask para el backend

\- MariaDB para el almacenamiento de información

\- API REST para la comunicación entre frontend y backend



\## Requisitos



Para ejecutar la aplicación se necesita:



1\. Flutter SDK instalado y configurado.

2\. Google Chrome para la ejecución web.

3\. Backend EV SERVICE funcionando.

4\. Base de datos MariaDB configurada.



\## Instalación del frontend



Clonar el repositorio:



```bash

git clone https://github.com/Edytp/ev\_service\_frontend.git

cd ev\_service\_frontend

```



Instalar las dependencias:



```bash

flutter pub get

```



Ejecutar la aplicación en Google Chrome:



```bash

flutter run -d chrome

```



\## Conexión con el backend



La aplicación se comunica con el servidor Flask mediante una API REST.



En la configuración actual de desarrollo, la dirección del backend es:



```text

http://localhost:5000

```



Para utilizar la aplicación en Chrome, el backend debe estar ejecutándose en el mismo equipo.



El archivo `lib/services/api\_service.dart` contiene la configuración de conexión con la API.



\## Repositorio del backend



https://github.com/Edytp/ev\_service\_backend



En este repositorio se encuentran el servidor Flask, las dependencias de Python, el archivo de configuración de ejemplo y la estructura de la base de datos MariaDB.



\## Finalidad académica



El proyecto EV SERVICE demuestra el desarrollo de una aplicación multiplataforma y su integración con un backend y una base de datos relacional.



La aplicación está diseñada como prototipo académico para su ejecución y demostración en un entorno local.

