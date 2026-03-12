import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

export function initMaps() {
    document.querySelectorAll('[data-map]').forEach(el => {
        const lat = parseFloat(el.dataset.lat);
        const lng = parseFloat(el.dataset.lng);
        const zoom = parseFloat(el.dataset.zoom) || 15;
        const style = el.dataset.style;
        if (!style || isNaN(lat) || isNaN(lng)) return;

        try {
            const map = new maplibregl.Map({
                container: el,
                style: style,
                center: [lng, lat],
                zoom: zoom,
                attributionControl: { compact: true },
                scrollZoom: false,
            });

            new maplibregl.Marker({ color: '#e74c3c' })
                .setLngLat([lng, lat])
                .addTo(map);

            map.addControl(new maplibregl.NavigationControl(), 'top-right');
        } catch {
            el.style.display = 'none';
            const fallback = el.nextElementSibling;
            if (fallback && fallback.classList.contains('map-fallback')) {
                fallback.style.display = '';
            }
        }
    });
}
