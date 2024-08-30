
    $(document).ready(function() {
        var map = L.map('map', {
            zoomControl: false // Disable the default zoom control to relocate it
        }).setView([7.188428, 124.533772], 18);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        // Add custom zoom control at the bottom right
        L.control.zoom({
            position: 'bottomright'
        }).addTo(map);

        // Custom search control
        var customSearchControl = L.Control.extend({
            onAdd: function(map) {
                var div = L.DomUtil.create('div', 'custom-search-card');
                div.innerHTML = `
                    <div class="search-header">
                        <form id="search-form" class="input-group">
                            <input id="search-input" type="text" class="form-control" placeholder="Search business">
                            <div class="input-group-append">
                                <button class="btn btn-primary" type="button" id="search-button">Search</button>
                            </div>
                        </form>
                    </div>
                    <div class="search-body">
                        <ul id="business-list" class="list-group">
                            <!-- List the Businesses here -->
                        </ul>
                    </div>`;
                return div;
            }
        });

        map.addControl(new customSearchControl({ position: 'topleft' }));

        var markers = {};
        var paymentModeLayers = {};
        var currentRadius = 6;

        // Define the circle marker styles with fill and border corresponding to the payment modes and payment status
        var getCircleOptions = function(paymentMode, paid, radius) {
            var options = {
                radius: radius || 6,  // Adjustable radius
                weight: 3,  // Increased border width
                opacity: 1,
                fillOpacity: 0.8
            };

            if (paid) {
                options.fillColor = '#0000FF'; // Blue fill for paid
            } else {
                options.fillColor = '#FF0000'; // Red fill for not paid
            }

            if (paymentMode === 'Quarterly') {
                options.color = '#00FFFF'; // Cyan border for Quarterly
            } else if (paymentMode === 'Annual') {
                options.color = '#FFFF00'; // Yellow border for Annual
            } else if (paymentMode === 'Bi-Annual') {
                options.color = '#00FF00'; // Green border for Bi-Annual
            } else {
                options.color = '#000'; // Default border color (black) if payment mode is unknown
            }

            return options;
        };

        function addMarkers(businesses) {
            console.log('Adding markers for businesses:', businesses); // Debug log
            for (var i = 0; i < businesses.length; i++) {
                var business = businesses[i];
                var circleOptions = getCircleOptions(business.payment_mode, business.paid, currentRadius);

                var marker = L.circleMarker([business.latitude, business.longitude], circleOptions)
                    .bindPopup(`<b>${business.name}</b><br>${business.location}<br>${business.picture_html}`)
                    .on('mouseover', function(e) { this.openPopup(); })
                    .on('mouseout', function(e) { this.closePopup(); });

                if (!paymentModeLayers[business.payment_mode]) {
                    paymentModeLayers[business.payment_mode] = L.layerGroup();
                }

                marker.addTo(paymentModeLayers[business.payment_mode]);
                markers[business.id] = marker;
            }
        }

        function loadBusinesses() {
            const businesses = JSON.parse('{{ businesses_json|escapejs }}');
            console.log('Loaded businesses:', businesses); // Debug log
            addMarkers(businesses);
            updateBusinessList(businesses);
        }

        function updateBusinessList(businesses) {
            console.log('Updating business list with:', businesses); // Debug log
            $('#business-list').empty();
            businesses.forEach(function(business) {
                console.log(`Adding business: ${business.name}, Payment Mode: ${business.payment_mode}`); // Debug log
                $('#business-list').append(`<li class="list-group-item" data-business-id="${business.id}" data-payment-mode="${business.payment_mode.trim()}">${business.name} - ${business.location}</li>`);
            });
            bindBusinessListClickEvent();
            if (businesses.length > 0) {
                $('#business-list').show(); // Show the business list when there are results
            } else {
                $('#business-list').hide(); // Hide the business list if no results
            }
        }

        function fetchSearchResults(searchQuery) {
            $.ajax({
                url: "{% url 'map-view' %}",
                data: { 'search': searchQuery },
                dataType: 'json',
                success: function(data) {
                    console.log('Search result data:', data); // Debug log
                    Object.keys(paymentModeLayers).forEach(function(mode) {
                        paymentModeLayers[mode].clearLayers();
                    });
                    addMarkers(data);
                    updateBusinessList(data);
                    updateFilteredBusinessList();
                }
            });
        }

        $('#search-input').on('input', function() {
            var searchQuery = $(this).val();

            if (searchQuery.trim() === '') {
                $('#business-list').hide(); // Hide the business list if search query is empty
                return;
            }

            fetchSearchResults(searchQuery);
        }).on('focus', function() {
            var searchQuery = $(this).val();
            if (searchQuery.trim() !== '') {
                $('#business-list').show(); // Show the business list if search query is not empty
            }
        });

        $('#search-button').on('click', function() {
            var searchQuery = $('#search-input').val();
            if (searchQuery.trim() === '') {
                $('#business-list').hide(); // Hide the business list if search query is empty
                return;
            }

            fetchSearchResults(searchQuery);
        });

        $(document).on('click', function(event) {
            if (!$(event.target).closest('.custom-search-card').length) {
                $('#business-list').hide(); // Hide the business list if clicking outside the search card
            }
        });

        function bindBusinessListClickEvent() {
            $('#business-list .list-group-item').on('click', function() {
                var businessId = $(this).data('business-id');
                var marker = markers[businessId];

                if (marker) {
                    marker.openPopup();
                    map.setView(marker.getLatLng(), 18);
                }
            });
        }

        // Add payment mode filters
        var overlayMaps = {};
        const paymentModes = ["Quarterly", "Annual", "Bi-Annual"];
        paymentModes.forEach(function(mode) {
            overlayMaps[mode] = paymentModeLayers[mode] || L.layerGroup();
        });

        var layersControl = L.control.layers(null, overlayMaps, { collapsed: false }).addTo(map);

        // Apply the custom styles to the checkboxes
        setTimeout(function() {
            $('.leaflet-control-layers-overlays label span').each(function() {
                var text = $(this).text().trim();
                if (text === 'Quarterly') {
                    $(this).siblings('input').addClass('checkbox-quarterly');
                } else if (text === 'Annual') {
                    $(this).siblings('input').addClass('checkbox-annual');
                } else if (text === 'Bi-Annual') {
                    $(this).siblings('input').addClass('checkbox-bi-annual');
                }
            });

            // Add custom controls
            $('.leaflet-control-layers-overlays').append(`
                <div class="tag">
                    <div class="circle renewed"></div>
                    <span>Renewed</span>
                </div>
                <div class="tag">
                    <div class="circle expired"></div>
                    <span>Expired</span>
                </div>
                <input type="range" id="radius-slider" min="2" max="20" value="6">
            `);

            // Radius control event listener
            $('#radius-slider').on('input', function() {
                currentRadius = $(this).val();
                Object.values(markers).forEach(function(marker) {
                    var options = marker.options;
                    options.radius = currentRadius;
                    marker.setStyle(options);
                });
            });
        }, 100);

        // Initial load of businesses
        loadBusinesses();

        // Filter markers and business list based on selected payment modes
        map.on('overlayadd', function(e) {
            var layerName = e.name;
            if (paymentModeLayers[layerName]) {
                paymentModeLayers[layerName].addTo(map);
            }
            updateFilteredBusinessList();
        });

        map.on('overlayremove', function(e) {
            var layerName = e.name;
            if (paymentModeLayers[layerName]) {
                map.removeLayer(paymentModeLayers[layerName]);
            }
            updateFilteredBusinessList();
        });

        function updateFilteredBusinessList() {
            var activeModes = [];
            $('.leaflet-control-layers-selector:checked').each(function() {
                activeModes.push($(this).next().text().trim());
            });
            console.log('Active payment modes:', activeModes); // Debug log

            $('#business-list .list-group-item').each(function() {
                var businessPaymentMode = $(this).data('payment-mode').trim();
                console.log('Business payment mode:', businessPaymentMode); // Debug log
                if (activeModes.includes(businessPaymentMode)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }

        // Add all payment mode layers to the map initially and check the checkboxes
        for (var mode in paymentModeLayers) {
            if (paymentModeLayers[mode]) {
                paymentModeLayers[mode].addTo(map);
                $('.leaflet-control-layers-selector + span:contains("' + mode + '")')
                    .prev().prop('checked', true);
            }
        }

        updateFilteredBusinessList();
    });