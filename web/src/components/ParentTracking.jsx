import React, {
  useEffect,
  useState,
} from "react";

import {
  GoogleMap,
  MarkerF,
  useJsApiLoader,
} from "@react-google-maps/api";

import { api } from "../api";


const mapContainerStyle = {
  width: "100%",
  height: "420px",
};


export default function ParentTracking() {
  const [children, setChildren] =
    useState([]);

  const [
    selectedChild,
    setSelectedChild,
  ] = useState(null);

  const [loc, setLoc] =
    useState(null);

  const [error, setError] =
    useState("");

  const [
    loadingLocation,
    setLoadingLocation,
  ] = useState(false);


  const {
    isLoaded,
    loadError,
  } = useJsApiLoader({
    googleMapsApiKey:
      import.meta.env
        .VITE_GOOGLE_MAPS_API_KEY || "",
  });


  async function loadLocation(
    studentId
  ) {
    if (!studentId) return;

    try {
      setLoadingLocation(true);
      setError("");

      const { data } =
        await api.get(
          `/api/v1/parents/children/${studentId}/location`
        );

      setLoc(data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Unable to load location."
      );
    } finally {
      setLoadingLocation(false);
    }
  }


  async function loadChildren() {
    try {
      setError("");

      const { data } =
        await api.get(
          "/api/v1/parents/children"
        );

      setChildren(data);

      if (data.length > 0) {
        setSelectedChild(
          data[0]
        );

        await loadLocation(
          data[0].id
        );
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err.message ||
          "Unable to load children."
      );
    }
  }


  useEffect(() => {
    loadChildren();
  }, []);


  /*
   * Refresh child location
   * every 15 seconds.
   */
  useEffect(() => {
    if (!selectedChild) return;

    const timer =
      setInterval(() => {
        loadLocation(
          selectedChild.id
        );
      }, 15000);

    return () =>
      clearInterval(timer);
  }, [selectedChild]);


  async function handleChildSelect(
    child
  ) {
    setSelectedChild(child);

    setLoc(null);

    await loadLocation(
      child.id
    );
  }


  const hasCoordinates =
    loc?.available &&
    typeof loc.latitude ===
      "number" &&
    typeof loc.longitude ===
      "number";


  const mapCenter =
    hasCoordinates
      ? {
          lat: loc.latitude,
          lng: loc.longitude,
        }
      : {
          lat: 16.5062,
          lng: 80.648,
        };


  function formatTime(
    date
  ) {
    if (!date) {
      return "Unknown";
    }

    try {
      return new Date(
        date
      ).toLocaleString();
    } catch {
      return date;
    }
  }


  return (
    <>
      {/* PAGE HEADER */}

      <div className="page-title">
        <div>
          <h1>
            Child Live Tracking
          </h1>

          <p>
            Monitor only children
            linked to your parent
            account.
          </p>
        </div>

        <button
          className="secondary"
          type="button"
          onClick={() => {
            if (
              selectedChild
            ) {
              loadLocation(
                selectedChild.id
              );
            }
          }}
        >
          Refresh Location
        </button>
      </div>


      {/* ERROR */}

      {error && (
        <div className="error">
          {error}
        </div>
      )}


      <div className="tracking-grid">

        {/* CHILD LIST */}

        <section className="panel">

          <div className="panel-title">
            <b>
              My Children
            </b>
          </div>


          {children.length ===
            0 && (
            <div className="readonly-note">
              No linked children
              found.
            </div>
          )}


          {children.map(
            (child) => {

              const active =
                selectedChild?.id ===
                child.id;

              return (
                <button
                  key={
                    child.id
                  }
                  type="button"
                  className={`child-card ${
                    active
                      ? "child-card-active"
                      : ""
                  }`}
                  onClick={() =>
                    handleChildSelect(
                      child
                    )
                  }
                >
                  <div className="avatar">
                    {child.name
                      ?.charAt(0)
                      ?.toUpperCase() ||
                      "S"}
                  </div>


                  <div>
                    <b>
                      {
                        child.name
                      }
                    </b>

                    <small>
                      {
                        child.relationship
                      }
                    </small>
                  </div>
                </button>
              );
            }
          )}

        </section>


        {/* TRACKING DETAILS */}

        <section className="panel">

          <div className="panel-title">
            <b>
              Current Safety
              Status
            </b>

            {loc?.available && (
              <span className="location-online">
                Live
              </span>
            )}
          </div>


          {loadingLocation && (
            <div className="readonly-note">
              Updating child
              location...
            </div>
          )}


          {!loadingLocation &&
          loc?.available ? (
            <>

              <h2>
                {loc.name}
              </h2>


              {/* STATUS CARDS */}

              <div className="tracking-status-grid">

                <div>
                  <small>
                    Status
                  </small>

                  <strong>
                    {
                      loc.status
                    }
                  </strong>
                </div>


                <div>
                  <small>
                    Tracking
                    Context
                  </small>

                  <strong>
                    {
                      loc.tracking_context
                    }
                  </strong>
                </div>


                <div>
                  <small>
                    Route
                  </small>

                  <strong>
                    {
                      loc.bus
                        ?.route ||
                      "—"
                    }
                  </strong>
                </div>


                <div>
                  <small>
                    Vehicle
                  </small>

                  <strong>
                    {
                      loc.bus
                        ?.vehicle ||
                      "—"
                    }
                  </strong>
                </div>


                <div>
                  <small>
                    ETA
                  </small>

                  <strong>
                    {loc.bus
                      ?.eta_minutes
                      ? `${loc.bus.eta_minutes} min`
                      : "—"}
                  </strong>
                </div>


                <div>
                  <small>
                    GPS Accuracy
                  </small>

                  <strong>
                    {loc.accuracy
                      ? `${Math.round(
                          loc.accuracy
                        )} m`
                      : "—"}
                  </strong>
                </div>

              </div>


              <p>
                <b>
                  Coordinates:
                </b>{" "}
                {
                  loc.latitude
                }
                ,{" "}
                {
                  loc.longitude
                }
              </p>


              <p>
                <b>
                  Last Updated:
                </b>{" "}
                {formatTime(
                  loc.recorded_at
                )}
              </p>


              {/* GOOGLE MAP */}

              {loadError ? (
                <div className="error">
                  Google Maps
                  could not be
                  loaded. Check
                  your Google
                  Maps API key.
                </div>
              ) : !isLoaded ? (
                <div className="map-placeholder">

                  <div>
                    Loading Map
                  </div>

                  <small>
                    Connecting to
                    Google Maps...
                  </small>

                </div>
              ) : (
                <div className="google-map-wrapper">

                  <GoogleMap

                    mapContainerStyle={
                      mapContainerStyle
                    }

                    center={
                      mapCenter
                    }

                    zoom={16}

                    options={{
                      streetViewControl:
                        false,

                      mapTypeControl:
                        false,

                      fullscreenControl:
                        true,

                      zoomControl:
                        true,
                    }}
                  >

                    <MarkerF
                      position={
                        mapCenter
                      }

                      title={
                        loc.name ||
                        "Student Location"
                      }
                    />

                  </GoogleMap>

                </div>
              )}

            </>
          ) : (
            !loadingLocation && (
              <div className="readonly-note">

                Location is
                currently
                unavailable for
                this child.

              </div>
            )
          )}

        </section>

      </div>
    </>
  );
}