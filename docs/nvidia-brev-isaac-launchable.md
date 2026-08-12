# NVIDIA Brev + Isaac Launchable: guía reproducible

Procedimiento completo para desplegar una GPU NVIDIA en Brev, recuperar Isaac Launchable si falla, abrir el viewer y ejecutar el Lab 01. Los comandos y diagnósticos provienen de una sesión real completada el 12 de agosto de 2026.

## Resultado de referencia

| Componente | Valor observado |
| --- | --- |
| Proveedor | AWS mediante NVIDIA Brev |
| GPU | NVIDIA L40S, aproximadamente `44.7 GiB` utilizables |
| CPU/RAM | 16 CPU, 128 GiB RAM |
| Driver remoto | `595.71.05` |
| CUDA reportada por el driver | `13.2` |
| Isaac Sim | `6.0.1` |
| Isaac Lab | `3.0.0-beta2-post1` / extensión `3.0.0` |
| Contenedor principal | `vscode` |
| Proyecto dentro del contenedor | `/workspace/space-minig-manufacturing` |
| Resultado | `3.928 m` en `8.01 s` a `120 grados/s` |

Estos valores describen la sesión de referencia, no requisitos permanentes. Brev puede cambiar disponibilidad, región, proveedor, precio e imágenes. Usa siempre el precio y las versiones mostradas al desplegar.

## Coste y seguridad

- Brev cobra mientras el entorno está activo; en la sesión observada el precio mostrado cambió según proveedor/pantalla y llegó a aproximadamente `$3.65/h`.
- Los `$10` de crédito no hacen gratis la instancia: representan cerca de 2–3 horas a ese precio.
- Verifica el indicador `$/hr` antes de pulsar **Deploy**.
- No publiques códigos de login, IP, hostname, URL privada del viewer ni credenciales.
- Haz `git push` antes de detener o eliminar la máquina.
- **Stop** conserva una instancia reiniciable; **Delete** destruye el almacenamiento de esa instancia.

## Mapa de terminales

Durante el procedimiento aparecen tres contextos. Reconócelos por el prompt:

| Contexto | Prompt aproximado | Qué se ejecuta allí |
| --- | --- | --- |
| Equipo local/WSL | `usuario@equipo:~/memo/...$` | `uv`, Git, `brev login`, `brev shell` |
| Host remoto Brev | `ubuntu@brev-...:~$` | Docker Compose y `docker exec` |
| Contenedor `vscode` | normalmente se usa mediante `docker exec` | Isaac Sim, Isaac Lab y repo en `/workspace` |

Los comandos de Docker se ejecutan en el **host remoto**, no en la terminal local y no dentro de otro contenedor.

## 1. Preparar y publicar el repositorio local

Desde la raíz local:

```bash
cd ~/memo/space-minig-manufacturing

uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py

git status --short
git diff --check
git add README.md AGENTS.md docs labs assets .gitignore
git commit -m "docs: document reproducible lunar rover workflow"
git push
```

Repositorio usado:

```text
https://github.com/gmgalvan/space-minig-manufacturing
```

El `.gitignore` debe excluir al menos `.venv`, caches Python, logs, editores y secretos locales.

## 2. Crear el entorno desde la página correcta

1. Abre [NVIDIA Brev](https://brev.nvidia.com/) e inicia sesión.
2. Revisa que haya crédito disponible.
3. Entra en **Launchables**, busca **Isaac Launchable** y abre su página.
4. Comprueba que la descripción incluye Isaac Sim e Isaac Lab.
5. Pulsa **Deploy Launchable**.
6. Selecciona una GPU RTX compatible. La sesión de referencia usó una **L40S**.
7. Elige región según disponibilidad; una región distinta no repara un lifecycle script defectuoso.
8. Asigna un nombre estable, por ejemplo `space-mining-lab-01`.
9. Lee el precio total por hora y pulsa **Deploy Launchable**.

No añadas Isaac Launchable desde el formulario genérico **Create Environment → Edit → Launchables** si devuelve:

```text
Error creating instance: rpc error: code = Internal desc = lifecycle script is empty
```

La ruta que funcionó fue abrir la página propia del Launchable y desplegar desde allí.

## 3. Esperar el aprovisionamiento

Estados esperados:

```text
Provisioned GPU instance
Configuring the instance
Run startup script
Check service status
```

En la página de la instancia:

```text
Compute: Running
VM Mode: Built
script: Executing → Completed
Secure Link: Loading → Healthy
```

El proceso puede tardar varios minutos porque construye imágenes y calienta cachés de Isaac Sim. Si el enlace se abre antes de que el servicio esté listo, es normal obtener:

```text
502 Bad Gateway
Host Error
```

Primero revisa el estado y los logs; refrescar repetidamente el navegador no inicia el backend.

## 4. Instalar Brev CLI en WSL/local

En la terminal **local**:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)"
export PATH="$HOME/.local/bin:$PATH"
brev login
```

Introduce el correo asociado a Brev. Si el navegador no se abre, copia la URL temporal mostrada y complétala en tu navegador. No guardes ni compartas esa URL.

Lista las instancias:

```bash
brev ls
```

Estado listo de referencia:

```text
NAME                 STATUS   BUILD      SHELL  GPU
space-mining-lab-01  RUNNING  COMPLETED  READY  L40S
```

Conéctate:

```bash
brev shell space-mining-lab-01
```

En el primer intento puede aparecer:

```text
Could not resolve hostname ...
Connection failed, refreshing SSH config and retrying...
```

Si Brev vuelve a intentarlo y terminas en `ubuntu@brev-...:~$`, la conexión fue correcta.

## 5. Verificar GPU y archivos del host remoto

Ya dentro del **host remoto**:

```bash
nvidia-smi
ls ~
```

`nvidia-smi` debe mostrar la GPU elegida. El Launchable debe haber creado:

```text
~/isaac-launchable/isaac-lab
```

Comprueba:

```bash
cd ~/isaac-launchable/isaac-lab
ls
docker compose ps
```

## 6. Camino feliz: lifecycle completado

Si el script aparece `Completed` y `docker compose ps` muestra `nginx`, `vscode` y `web-viewer` activos, salta a la sección 8.

Servicios esperados:

```text
isaac-lab-nginx-1
vscode
web-viewer
```

El contenedor `vscode` puede aparecer unos segundos como `health: starting`. Espera y vuelve a ejecutar:

```bash
docker compose ps
```

## 7. Recuperación cuando el lifecycle script falla

### Síntomas observados

- la máquina está `Running` y `VM Mode` está `Built`;
- `script` termina en `Failed`;
- Secure Link está `Unhealthy`;
- `docker compose ps` no muestra servicios;
- no existe `isaac-sim.sh` en el home del host.

La ausencia de `~/isaac-sim.sh` no significa que Isaac Sim no esté en la imagen. Vive dentro del contenedor `vscode`, bajo `/isaac-sim`.

### Causa observada

El lifecycle script contenía:

```bash
dockercompose up -d
```

El comando correcto lleva un espacio:

```bash
docker compose up -d
```

### Levantar servicios manualmente

En el host remoto:

```bash
cd ~/isaac-launchable/isaac-lab
docker compose up -d
docker compose ps
```

Durante la construcción es normal ver varios minutos de descarga/build. También puede aparecer:

```text
The "DEV_NGINX_PORT" variable is not set
Published ports are discarded when using host network mode
```

En la sesión de referencia esas advertencias no impidieron iniciar los tres servicios.

### Completar la preparación que omitió el lifecycle

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

El warmup corre en primer plano. No presiones `Ctrl+C` mientras continúe cargando extensiones. Espera hasta ver:

```text
Simulation App Startup Complete
app ready
[INFO]: Setup complete...
[INFO] Using Python: "/workspace/isaaclab/_isaac_sim/python.sh"
```

Cuando vuelve el prompt del host, terminó. Si queda intencionalmente abierto después de `app ready`, `Ctrl+C` es válido; confirma que volvió el prompt antes del siguiente comando.

## 8. Clonar o actualizar el proyecto dentro del contenedor

Desde el host remoto:

```bash
docker exec -u ubuntu vscode bash -lc '
  if [ -d /workspace/space-minig-manufacturing/.git ]; then
    cd /workspace/space-minig-manufacturing && git pull --ff-only
  else
    cd /workspace && git clone https://github.com/gmgalvan/space-minig-manufacturing.git
  fi
'
```

Verifica:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git status --short && ls labs/01-lunar-rover'
```

No vuelvas a ejecutar `git clone` si el directorio ya existe; usa `git pull --ff-only`.

## 9. Abrir el viewer

En la página Brev, abre el enlace llamado **isaac**. Si abre la raíz o una página vacía, añade:

```text
/viewer/
```

El viewer puede mostrar `WAITING FOR STREAM` mientras no exista un proceso Isaac Sim con livestream. Esto es correcto: primero deja abierta esa pestaña y luego lanza el script desde SSH.

## 10. Ejecutar el rover

### Inspección sin motores

En el host remoto:

```bash
cd ~/isaac-launchable/isaac-lab

docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/run_lunar_rover.py --livestream 2 --viz kit'
```

Espera `app ready` y:

```text
[INFO]: Escena lunar abierta: .../lunar_rover_scene_v0.usda
[INFO]: Simulación activa; detener con Ctrl+C.
```

Regresa al viewer. Debes ver `World`, `PhysicsScene`, `LunarGround` y `LunarRover`. El script ya activa la línea de tiempo; no necesitas encontrar un botón Play.

### Tracción y medición

Detén la inspección anterior con `Ctrl+C`. Después:

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 8 --wheel-speed 120'
```

Resultado de referencia:

```text
[DEBUG]: Motor configurado: /World/LunarRover/Joints/FrontLeftAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/FrontRightAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/RearLeftAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/RearRightAxle
[INFO]: Motores activos durante 8.0 s.
[RESULT]: desplazamiento=3.928 m; duración=8.01 s
[INFO]: La escena queda abierta para inspección. Detener con Ctrl+C.
```

El movimiento ocurre durante los primeros ocho segundos. Después la línea de tiempo se detiene y la escena permanece abierta. Presiona `Ctrl+C` cuando termines de inspeccionarla.

## 11. Sincronización para iterar

Flujo corto para cambios posteriores:

En local:

```bash
git add <archivos>
git commit -m "descripcion del cambio"
git push
```

En el host Brev:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

Luego repite el comando de tracción. No hace falta reconstruir los contenedores por cambios en scripts o `.usda` del proyecto.

## 12. Diagnóstico rápido

### ¿Los contenedores siguen activos?

```bash
cd ~/isaac-launchable/isaac-lab
docker compose ps
```

### ¿El contenedor ve la GPU?

```bash
docker exec vscode nvidia-smi
```

### ¿Hay un Isaac Sim ejecutándose?

```bash
docker exec vscode bash -lc "ps -ef | grep -E '[k]it|[i]saac'"
```

### Logs recientes

```bash
docker compose logs --tail=200
docker logs --tail=200 vscode
docker logs --tail=200 web-viewer
```

### Confirmar el repo y commit usados

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git status --short && git rev-parse --short HEAD'
```

## 13. Tabla de problemas conocidos

| Síntoma | Causa probable | Acción |
| --- | --- | --- |
| `lifecycle script is empty` al desplegar | integración defectuosa en formulario genérico | desplegar desde la página propia de Isaac Launchable |
| lifecycle `Failed` | `dockercompose` sin espacio | ejecutar `docker compose up -d` y el warmup manual |
| `502 Bad Gateway` | backend del puerto 80 aún no está listo | comprobar contenedores/logs y esperar |
| Secure Link `Unhealthy` | nginx o viewer sin backend | ejecutar `docker compose ps` y revisar logs |
| `WAITING FOR STREAM` | no hay Isaac Sim transmitiendo | ejecutar `run_lunar_rover.py` o `drive_lunar_rover.py` |
| `Got stop event while waiting for client connection` | proceso detenido o sesión livestream en conflicto | cerrar procesos previos, abrir viewer y relanzar uno solo |
| `GLFW initialization failed` | sesión headless sin ventana local | aceptable si el WebRTC y el resultado funcionan |
| `Failed to open /var/run/utmp` | entorno contenedorizado sin sesión de escritorio | aceptable si continúa hasta `app ready` |
| `joint with disjointed body transforms` | anclas de junta incorrectas | actualizar repo, regenerar USD y no aceptar esa corrida |
| cambios no aparecen | se actualizó el host, no `/workspace` | hacer `git pull` dentro de `vscode` |
| `destination path already exists` | repo ya clonado | usar `git pull --ff-only` |

## 14. Cerrar sin perder trabajo

1. En la terminal que ejecuta Isaac Sim, presiona `Ctrl+C`.
2. Confirma que regresó el prompt.
3. Publica cambios desde el contenedor o, preferiblemente, desde la copia local controlada.
4. Escribe `exit` para salir de SSH.
5. En la página Brev pulsa **Stop** si la instancia lo permite.
6. Confirma que el estado dejó de ser `Running` y que ya no se acumula coste de cómputo.

Usa **Delete** sólo cuando hayas guardado todo y aceptes perder el disco remoto. Algunas configuraciones no admiten Stop/Restart; en ese caso Brev lo indica explícitamente y la única forma de terminar el cobro puede ser eliminar la instancia.

## Checklist de reproducción

- [ ] Repositorio local generado, validado y publicado.
- [ ] Crédito y precio horario revisados.
- [ ] Isaac Launchable desplegado desde su página propia.
- [ ] `brev ls` muestra `RUNNING / COMPLETED / READY` o se aplicó recuperación manual.
- [ ] `nvidia-smi` reconoce la GPU en host/contenedor.
- [ ] `nginx`, `vscode` y `web-viewer` están activos.
- [ ] Repo actualizado dentro de `/workspace`.
- [ ] Viewer abierto en `/viewer/`.
- [ ] Cuatro motores configurados.
- [ ] Resultado de desplazamiento registrado.
- [ ] Proceso cerrado y coste detenido al finalizar.
