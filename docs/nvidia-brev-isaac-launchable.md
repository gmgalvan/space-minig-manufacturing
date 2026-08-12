# Ejecutar el Lab 01 en NVIDIA Brev con Isaac Launchable

Guía operativa para abrir el rover lunar de este repositorio en una GPU NVIDIA L40S en la nube. El flujo usa **NVIDIA Brev**, el **Isaac Launchable** oficial y acceso por SSH desde WSL.

> Coste y seguridad: Brev cobra mientras la instancia está activa. Revisa el precio antes de desplegar y detén o elimina la instancia al terminar. No publiques direcciones IP, URLs de acceso ni códigos temporales de inicio de sesión.

## 1. Preparar el repositorio local

Antes de crear una GPU remota, confirma que el proyecto está publicado en GitHub y que no incluye el entorno virtual local.

Archivos requeridos para este laboratorio:

```text
assets/usd/robots/lunar_rover_v0.usda
assets/usd/robots/lunar_rover_physics_v0.usda
labs/01-lunar-rover/lunar_rover_scene_v0.usda
labs/01-lunar-rover/scripts/
```

El repositorio público actual se puede clonar con:

```bash
git clone https://github.com/gmgalvan/space-minig-manufacturing.git
```

## 2. Crear la instancia en Brev

1. Iniciar sesión en [NVIDIA Brev](https://brev.nvidia.com/).
2. Abrir **GPUs** y seleccionar una **NVIDIA L40S**.
3. Para Isaac Sim, elegir una GPU con RT Cores y VRAM suficiente. La L40S tiene aproximadamente 44–48 GiB de VRAM según el proveedor.
4. En vez de insertar la plantilla desde la pantalla genérica *Create Environment*, abrir **Launchables** y buscar **Isaac Launchable**.
5. Abrir su página propia y seleccionar **Deploy Launchable**.
6. Asignar un nombre, por ejemplo:

   ```text
   space-mining-lab-01
   ```

7. Confirmar el coste horario mostrado por Brev y desplegar.

La ruta directa del Launchable importa porque incluye el repositorio `isaac-launchable` y su script de arranque. En esta sesión, añadir la plantilla desde la pantalla genérica produjo el error `lifecycle script is empty`.

## 3. Esperar los estados correctos

En la página de la instancia, comprobar la progresión:

```text
GPU instance: Provisioned / Running
VM mode: Built
Lifecycle script: Executing → Completed
Secure link health: Loading → Healthy
```

No abrir el enlace de Isaac mientras la salud sea `Unavailable` o `Unhealthy`: una página `502 Bad Gateway` sólo indica que el servicio de origen aún no está listo.

## 4. Instalar Brev CLI y autenticar desde WSL

En una terminal WSL local, instalar la CLI oficial y abrir sesión:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)"
brev login
```

El inicio de sesión puede mostrar una URL temporal si el navegador no se abre automáticamente. Completarla sólo en el navegador propio.

Comprobar la instancia:

```bash
brev ls
```

Una instancia lista debe mostrar valores equivalentes a:

```text
NAME                 STATUS   BUILD      SHELL  GPU
space-mining-lab-01  RUNNING  COMPLETED  READY  L40S
```

Entrar por SSH:

```bash
brev shell space-mining-lab-01
```

En el primer intento puede aparecer una resolución de host fallida y Brev puede refrescar su configuración SSH. Si después muestra un prompt como `ubuntu@brev-...`, la conexión quedó lista.

Validar la GPU remota:

```bash
nvidia-smi
```

Esperado: una `NVIDIA L40S` con alrededor de 46 GiB utilizables de memoria.

## 5. Copiar el proyecto al host de Brev

Dentro de la sesión SSH remota:

```bash
git clone https://github.com/gmgalvan/space-minig-manufacturing.git
cd space-minig-manufacturing
ls labs/01-lunar-rover
```

Esto deja una copia del proyecto en el host. Más adelante se clonará además dentro del contenedor `vscode`, que es donde se ejecuta Isaac Sim.

## 6. Recuperación manual si falla el Lifecycle Script

### Síntoma

La instancia queda `Running`, pero el script pasa a `Failed`, el enlace seguro aparece `Unhealthy` y no hay contenedores activos:

```bash
cd ~/isaac-launchable/isaac-lab
docker compose ps
```

En esta sesión, la plantilla contenía `dockercompose up -d` (sin espacio), por lo que nunca ejecutó Docker Compose.

### Levantar los servicios

Desde el host remoto, ejecutar el comando correcto:

```bash
cd ~/isaac-launchable/isaac-lab
docker compose up -d
docker compose ps
```

Se deben iniciar estos contenedores:

```text
isaac-lab-nginx-1
vscode
web-viewer
```

Es posible ver la advertencia `DEV_NGINX_PORT variable is not set`; no bloqueó el levantamiento de los contenedores en este caso.

### Completar manualmente la preparación de Isaac Sim

El script interrumpido también debía preparar permisos y calentar Isaac Sim. Ejecutar desde el mismo host SSH:

```bash
docker exec -u root vscode sed -i \
  -e 's|^PORTABLE_ROOT="$SCRIPT_DIR/portable_root"$|PORTABLE_ROOT="$SCRIPT_DIR/kit"|' \
  -e 's|emptyStageOnStart=1|emptyStageOnStart=0|' \
  /isaac-sim/warmup.sh

docker exec -u root vscode install -d -o ubuntu -g ubuntu \
  /isaac-sim/kit/cache \
  /isaac-sim/kit/data \
  /isaac-sim/kit/logs \
  /root/.cache \
  /root/.nv/ComputeCache

docker exec -u ubuntu:ubuntu -w /isaac-sim vscode ./warmup.sh
```

El último comando puede tardar varios minutos. Mensajes sobre la ausencia de X Server, OmniHub o `CUDA_VISIBLE_DEVICES` son habituales en un arranque remoto/headless; esperar a que el proceso termine o revisar el final del log si termina con error.

## 7. Clonar el proyecto dentro del contenedor Isaac

Cuando el contenedor `vscode` esté en ejecución, desde el host remoto ejecutar:

```bash
docker exec -u ubuntu vscode bash -lc '\
  cd /workspace && \
  git clone https://github.com/gmgalvan/space-minig-manufacturing.git && \
  cd space-minig-manufacturing && \
  ls labs/01-lunar-rover && \
  ls /isaac-sim'
```

El proyecto quedará disponible en:

```text
/workspace/space-minig-manufacturing
```

El archivo de escena que se abrirá en Isaac Sim es:

```text
/workspace/space-minig-manufacturing/labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

## 8. Próximo procedimiento

Una vez terminado el warmup:

1. Lanzar Isaac Sim con livestream desde el contenedor `vscode`.
2. Abrir `lunar_rover_scene_v0.usda`.
3. Confirmar terreno, gravedad lunar, cuerpos rígidos y cuatro juntas de rueda.
4. Añadir actuadores a las juntas y ejecutar la primera maniobra: avanzar, girar y detenerse.

## 9. Cierre de sesión y coste

- Guardar y hacer `git push` de cualquier cambio importante antes de cerrar.
- Detener la instancia si Brev/proveedor lo permite.
- Si la instancia es de tipo no reiniciable, usar **Delete** al terminar: los datos de la máquina se perderán, pero el repositorio remoto conservará el trabajo publicado.
