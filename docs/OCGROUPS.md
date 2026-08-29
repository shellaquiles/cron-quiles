# Agregar soporte para nuevos feeds y grupos de ocgroups.dev

Para agregar un grupo de [ocgroups.dev](https://ocgroups.dev) (como comunidades de CNCF u Open Source communities):

1. El agregador `OCGroupsAggregator` en `src/cronquiles/aggregators/ocgroups.py` maneja la extracción e introspección de eventos desde páginas de grupo como `https://ocgroups.dev/cncf/group/{id}`.
2. Agrega la entrada a `config/feeds.yaml`:
   ```yaml
   - url: https://ocgroups.dev/cncf/group/e5vgp72
     name: Cloud Native Mexico City
     description: CNCF community in Open Community Groups (Ciudad de México).
   ```
3. `ics_aggregator.py` detectará automáticamente URLs con `ocgroups.dev` y delegará a `OCGroupsAggregator`.
