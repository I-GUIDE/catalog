<template>
  <v-card class="cd-spatial-coverage-map">
    <div ref="map" class="map-container"></div>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Prop, Ref } from "vue-property-decorator";
import { Loader, LoaderOptions } from "google-maps";

const DEFAULT_ZOOM = 5;

@Component({
  name: "cd-spatial-coverage-map",
  components: {},
})
export default class CdSpatialCoverageMap extends Vue {
  @Prop() feature!: any;
  @Prop() loader!: Loader;
  @Prop() loaderOptions!: LoaderOptions;

  @Ref("map") mapContainer;
  protected map: google.maps.Map | null = null;
  protected markers: google.maps.Marker[] = [];
  protected rectangles: google.maps.Rectangle[] = [];
  protected markerOptions: google.maps.MarkerOptions = {};
  protected rectangleOptions: google.maps.RectangleOptions = {};

  async mounted() {
    await this.initMap();
    this.loadDrawing();
    if (this.map) {
      const bounds = new google.maps.LatLngBounds();
      this.markers.forEach((marker) => {
        const pos = marker.getPosition() as google.maps.LatLng;
        bounds.extend(new google.maps.LatLng(pos.lat(), pos.lng()));
      });

      this.map.fitBounds(bounds);

      if (this.markers.length === 1) {
        // For single point coverages, use default zoom
        const map = this.map;
        setTimeout(() => {
          map.setZoom(DEFAULT_ZOOM);
        }, 100);
      }

      // TODO: check if this overrides the marker bounds
      this.rectangles.forEach((rectangle) => {
        this.map?.fitBounds(rectangle.getBounds());
      });
    }
  }

  created() {}

  protected async initMap() {
    const google = await this.loader.load();

    this.map = new google.maps.Map(this.mapContainer, {
      center: { lat: 39.8097343, lng: -98.5556199 },
      zoom: DEFAULT_ZOOM,
      gestureHandling: "greedy",
    });

    // Icon base from: http://kml4earth.appspot.com/icons.html
    const iconBase = "http://earth.google.com/images/kml-icons/";
    const icons = {
      track_directional: {
        icon: iconBase + "track-directional/track-8.png",
      },
    };

    this.markerOptions = {
      ...this.markerOptions,
      // animation: google.maps.Animation.DROP,
      icon: {
        url: icons.track_directional.icon,
        anchor: new google.maps.Point(20, 35),
        scaledSize: new google.maps.Size(40, 40),
      },
    };

    this.rectangleOptions = {
      ...this.rectangleOptions,
      fillColor: "#1976d2",
      fillOpacity: 0.25,
      strokeWeight: 2,
      strokeColor: "#1976d2",
      editable: false,
      zIndex: 1,
      draggable: false,
    };
  }

  protected loadDrawing() {
    if (this.feature) {
      if (this.feature["@type"] === "GeoCoordinates") {
        const point: google.maps.ReadonlyLatLngLiteral = {
          lat: this.feature.latitude,
          lng: this.feature.longitude,
        } as google.maps.ReadonlyLatLngLiteral;
        this.loadMarkers([point]);
      } else if (this.feature["@type"] === "GeoShape") {
        const extents = this.feature.box
          .trim()
          .split(" ")
          .map((n) => +n);
        if (extents.length === 4) {
          const rectangle: google.maps.LatLngBoundsLiteral = {
            north: extents[0],
            east: extents[1],
            south: extents[2],
            west: extents[3],
          } as google.maps.LatLngBoundsLiteral;
          this.loadRectangles([rectangle]);
        }
      }
    }
  }

  protected clearMarkers() {
    if (this.markers.length) {
      this.markers.forEach((m) => {
        m.setMap(null);
      });
      this.markers = [];
    }
  }

  protected loadMarkers(markers: google.maps.ReadonlyLatLngLiteral[]) {
    if (this.map) {
      this.clearMarkers();

      markers.forEach((m) => {
        const marker = new google.maps.Marker({
          ...this.markerOptions,
          position: { lat: m.lat, lng: m.lng },
          map: this.map as google.maps.Map,
        });

        this.markers.push(marker);
      });
    }
  }

  protected clearRectangles() {
    if (this.rectangles.length) {
      this.rectangles.forEach((r) => {
        r.setMap(null);
      });
      this.rectangles = [];
    }
  }

  protected loadRectangles(rectangles: google.maps.LatLngBoundsLiteral[]) {
    if (this.map) {
      this.clearRectangles();

      rectangles.forEach((r) => {
        const rectangle = new google.maps.Rectangle({
          ...this.rectangleOptions,
          bounds: r,
          map: this.map as google.maps.Map,
        });

        this.rectangles.push(rectangle);
      });
    }
  }
}
</script>

<style lang="scss" scoped>
.map-container {
  min-width: 20rem;
  min-height: 10rem;
}

.cd-spatial-coverage-map {
  padding: 2px;
}
</style>
