# Anatomía del Despliegue (Deployment Internals)

La parte más sensible de este repositorio vive dentro del `Makefile` bajo el target **`deploy-gh-pages`**. Esta es la arteria de distribución del código por la que se comunica el Github Action CI/CD.

## ¿Cómo funciona el despliegue?
1. Copia el contenido de la carpeta `/gh-pages/` (el código frontend).
2. Arrastra y embebe el output que el pipeline compiló (el `history.json`, y los subarchivos dentro de `/data/`).
3. Hace switch (checkout) de Git a una rama especial **orphan** llamada `gh-pages`.
4. Limpia la rama entera, inyecta la carpeta compilada temporalmente y realiza un "force push" (`git push origin gh-pages --force`).

## 🛑 Regla de Oro (HARD STOP)
NUNCA asumas que puedes refactorizar `deploy-gh-pages` o alterar las rutas físicas de `/data/` a menos que sea una directiva de rediseño de arquitectura completa pedida por el usuario. Romper los copies temporales del Makefile significa matar el sitio de producción instantáneamente.
