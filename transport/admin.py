from django.contrib import admin
from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, StackedInline
from .models import Unit, Route, Stop, Ticket
from services.models import Service



# --- ICONOS SVG ---
ICON_TRUCK = '<svg class="w-5 h-5 inline-block mr-2 -mt-1 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 0 0-3.213-9.193 2.056 2.056 0 0 0-1.58-.806H14.25M16.5 18.75h-2.25m0-11.177V3.75A2.25 2.25 0 0 0 12 1.5H1.5a2.25 2.25 0 0 0-2.25 2.25v13.125c0 .621.504 1.125 1.125 1.125H3.375m9.375-1.125V4.688A2.25 2.25 0 0 1 15 2.438h2.25" /></svg>'
ICON_CASH = '<svg class="w-5 h-5 inline-block mr-2 -mt-1 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5h16.5m-18 3h18m-18 3h18m-18 3h18m-11.25 3h.008v.008h-.008V15Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM12 15.75h.007v.008H12v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm2.25-3h.008v.008h-.008v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" /></svg>'
ICON_STARS = '<svg class="w-5 h-5 inline-block mr-2 -mt-1 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" /></svg>'


class ServiceGalleryWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        services = Service.objects.all().select_related('tienda')

        extra_css = '''
        <style>
            /* Contenedor principal para forzar la pila vertical */
            .gallery-wrapper { display: flex !important; flex-direction: column !important; width: 100% !important; gap: 1rem; }

            /* Buscador Full-Width arriba */
            .gallery-search-area { width: 100% !important; display: block !important; order: 1; }
            #service-search { width: 100% !important; min-height: 48px !important; border-radius: 12px !important; border: 1.5px solid #cbd5e1 !important; padding: 0 12px 0 48px !important; font-size: 14px !important; }

            /* Galería abajo */
            .gallery-grid-area { order: 2; width: 100% !important; }
            .services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1.25rem; max-height: 550px; overflow-y: auto; padding: 10px; background: #f1f5f9; border-radius: 14px; border: 1px solid #e2e8f0; }

            /* Ocultar checkbox e interacción de tarjeta */
            .service-card input[type="checkbox"] { display: none !important; }
            .service-card input:checked + .card-content { border-color: #059669 !important; background-color: #f0fdf4 !important; box-shadow: 0 0 0 3px #059669 !important; }
            .service-card input:checked + .card-content .check-badge { display: flex !important; }
        </style>
        '''

        # Estructura HTML con IDs y clases claras para el orden
        # Estructura HTML con el icono ACUÑADO dentro del buscador
        search_html = f'''
                <div class="gallery-wrapper">
                    <div class="gallery-search-area">
                        <div style="position: relative; display: flex; align-items: center; width: 100%;">
                            <div style="position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; display: flex; align-items: center; z-index: 10;">
                                <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                </svg>
                            </div>
                            <input type="text" id="service-search" placeholder="Buscar entre miles de servicios (Hotel, Surf, Café)..." 
                                   class="bg-white" style="padding-left: 48px !important; width: 100% !important;">
                        </div>
                    </div>
                '''

        grid_html = '<div class="gallery-grid-area"><div id="services-grid" class="services-grid">'

        for service in services:
            is_checked = value and str(service.id) in map(str, value)
            checked_attr = 'checked' if is_checked else ''
            img_url = service.imagen_principal.url if service.imagen_principal else "https://via.placeholder.com/150?text=Servicio"

            grid_html += f'''
                <label class="service-card relative cursor-pointer block h-full">
                    <input type="checkbox" name="{name}" value="{service.id}" {checked_attr}>
                    <div class="card-content border-2 border-white rounded-2xl overflow-hidden transition-all duration-300 bg-white shadow-sm hover:shadow-md h-full" 
                         data-search="{service.nombre.lower()} {service.tienda.nombre_comercial.lower()}">
                        <div class="aspect-video w-full overflow-hidden bg-gray-50">
                            <img src="{img_url}" loading="lazy" class="w-full h-full object-cover">
                        </div>
                        <div class="p-3 text-center">
                            <p class="text-[11px] font-bold text-gray-800 uppercase truncate leading-tight">{service.nombre}</p>
                            <p class="text-[9px] text-gray-500 font-medium truncate mt-1">{service.tienda.nombre_comercial}</p>
                        </div>
                        <div class="check-badge absolute top-2 right-2 hidden w-6 h-6 bg-primary-500 text-white rounded-full items-center justify-center shadow-lg border-2 border-white">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                        </div>
                    </div>
                </label>
            '''

        grid_html += '</div></div></div>'

        js_script = '''
        <script>
            document.getElementById('service-search').addEventListener('input', function(e) {
                const term = e.target.value.toLowerCase();
                document.querySelectorAll('.service-card').forEach(card => {
                    const content = card.querySelector('.card-content').getAttribute('data-search');
                    card.style.display = content.includes(term) ? 'block' : 'none';
                });
            });
        </script>
        '''

        return mark_safe(extra_css + search_html + grid_html + js_script)


class RouteAdminForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = '__all__'
        widgets = {'included_services': ServiceGalleryWidget()}


class StopInline(StackedInline):
    model = Stop
    extra = 1
    fields = ('name', 'order', 'minutes_from_start', ('latitude', 'longitude'), 'map_picker')
    readonly_fields = ('map_picker',)

    def map_picker(self, obj):
        brand_color = "#059669"
        lat = obj.latitude if obj.latitude is not None else 13.6843
        lng = obj.longitude if obj.longitude is not None else -89.2191

        return mark_safe(f'''
            <div class="map-system-container" style="width: 100%; margin-bottom: 20px;">
                <div style="margin-bottom: 12px; display: flex; gap: 10px;">
                    <input type="text" class="map-search-input" placeholder="Escribe la dirección..." 
                        style="flex: 1; padding: 12px; border-radius: 8px; border: 2px solid #cbd5e1; font-size: 14px; background: white; color: black;">
                    <button type="button" class="map-search-btn" 
                        style="background: {brand_color}; color: white; padding: 0 24px; border-radius: 8px; font-weight: 700; cursor: pointer; border: none; text-transform: uppercase;">
                        BUSCAR
                    </button>
                </div>

                <div class="leaflet-map-real-instance" 
                    data-lat="{lat}" data-lng="{lng}"
                    style="height: 400px; width: 100%; border-radius: 12px; border: 2px solid {brand_color}; background: #f8fafc; position: relative;">
                </div>
            </div>

            <script>
                (function() {{
                    const initSingleMap = (mapEl) => {{
                        if (!mapEl || mapEl._leaflet_id) return;

                        const lat = parseFloat(mapEl.dataset.lat);
                        const lng = parseFloat(mapEl.dataset.lng);

                        const map = L.map(mapEl).setView([lat, lng], 15);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);

                        const pin = L.divIcon({{
                            html: `<svg width="32" height="42" viewBox="0 0 24 24" fill="none"><path d="M12 21.325C12 21.325 19 15.3533 19 10.0417C19 6.15262 15.8655 3 12 3C8.13452 3 5 6.15262 5 10.0417C5 15.3533 12 21.325 12 21.325Z" fill="{brand_color}" stroke="#064e3b" stroke-width="1.5"/><circle cx="12" cy="10" r="3" fill="white"/></svg>`,
                            className: 'custom-pin', iconSize: [32, 42], iconAnchor: [16, 42]
                        }});

                        const marker = L.marker([lat, lng], {{ icon: pin, draggable: true }}).addTo(map);

                        marker.on('dragend', function() {{
                            const pos = marker.getLatLng();
                            const row = mapEl.closest('.unfold-card, .inline-related, fieldset');
                            if (row) {{
                                row.querySelector('input[name*="latitude"]').value = pos.lat.toFixed(6);
                                row.querySelector('input[name*="longitude"]').value = pos.lng.toFixed(6);
                            }}
                        }});

                        const container = mapEl.closest('.map-system-container');
                        const btn = container.querySelector('.map-search-btn');
                        const input = container.querySelector('.map-search-input');

                        btn.onclick = async () => {{
                            const q = input.value;
                            if (!q) return;
                            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${{encodeURIComponent(q)}}`);
                            const data = await res.json();
                            if (data.length > 0) {{
                                const pos = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
                                map.setView(pos, 16);
                                marker.setLatLng(pos);
                                const row = mapEl.closest('.unfold-card, .inline-related, fieldset');
                                row.querySelector('input[name*="latitude"]').value = pos[0].toFixed(6);
                                row.querySelector('input[name*="longitude"]').value = pos[1].toFixed(6);
                            }}
                        }};

                        let counts = 0;
                        const fixSize = setInterval(() => {{
                            map.invalidateSize();
                            counts++;
                            if (counts > 15) clearInterval(fixSize);
                        }}, 300);
                    }};

                    document.querySelectorAll('.leaflet-map-real-instance').forEach(initSingleMap);

                    const observer = new MutationObserver((mutations) => {{
                        mutations.forEach((mutation) => {{
                            mutation.addedNodes.forEach((node) => {{
                                if (node.nodeType === 1) {{
                                    const newMaps = node.querySelectorAll('.leaflet-map-real-instance');
                                    newMaps.forEach(m => setTimeout(() => initSingleMap(m), 100));
                                    if (node.classList.contains('leaflet-map-real-instance')) {{
                                        setTimeout(() => initSingleMap(node), 100);
                                    }}
                                }}
                            }});
                        }});
                    }});

                    observer.observe(document.body, {{ childList: true, subtree: true }});
                }})();
            </script>
        ''')

    map_picker.short_description = "Selector de Ubicación"

    class Media:
        css = {'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)}
        js = ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',)
    classes = ("unfold-card",)


@admin.register(Route)
class RouteAdmin(ModelAdmin):
    form = RouteAdminForm
    fieldsets = (
        (mark_safe(ICON_TRUCK + ' Logística de la Ruta'), {'fields': ('name', 'unit', 'is_active')}),
        (mark_safe(ICON_CASH + ' Tarifas Comerciales'), {'fields': (('price_one_way', 'price_round_trip'),)}),
        (mark_safe(ICON_STARS + ' Galería de Servicios Incluidos'), {
            'fields': ('included_services',),
        }),
    )
    list_display = ('name', 'unit', 'price_one_way', 'price_round_trip', 'is_active')
    list_filter = ('is_active', 'unit')
    search_fields = ('name',)
    inlines = [StopInline]
    autocomplete_fields = ['unit']


@admin.register(Unit)
class UnitAdmin(ModelAdmin):
    list_display = ('name', 'license_plate', 'capacity')
    search_fields = ('name', 'license_plate')
    ordering = ('name',)


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('id', 'user', 'route', 'ticket_type', 'total_paid', 'is_used')
    list_filter = ('ticket_type', 'is_used', 'purchase_date')
    readonly_fields = ('purchase_date',)
    autocomplete_fields = ['user', 'route']