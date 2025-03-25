import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";
import * as gcp from "@pulumi/gcp";
import * as dotenv from "dotenv";

dotenv.config();

// Obtener configuración
const config = new pulumi.Config("gcp");
const project = config.require("project");
const region = config.get("region") || "us-central1";

// Obtener variables de entorno desde la configuración de Pulumi
const apifyToken = config.requireSecret("apifyToken");
const backendUrl = config.requireSecret("backendUrl");

// Configuración del registro (usando GCR en este ejemplo)
const registryInfo = {
  server: "gcr.io",
  username: "_json_key",
  // La contraseña es la clave JSON en formato string
  password: process.env.GCP_SERVICE_ACCOUNT_KEY,
};

// Construir y subir la imagen del Backend
const backendImage = new docker.Image("backendImage", {
  build: {
    context: "../backend",
  },
  imageName: pulumi.interpolate`gcr.io/${project}/backend:latest`,
  registry: registryInfo,
});

// Construir y subir la imagen del Frontend
const frontendImage = new docker.Image("frontendImage", {
  build: {
    context: "../frontend_v2",
  },
  imageName: pulumi.interpolate`gcr.io/${project}/frontend:latest`,
  registry: registryInfo,
});

// Crear servicio de Cloud Run para el Backend usando la imagen construida
const backendService = new gcp.cloudrun.Service("backendService", {
  location: region,
  template: {
    spec: {
      containers: [
        {
          image: backendImage.imageName,
          ports: [{ containerPort: 8080 }],
          envs: [
            {
              name: "APIFY_API_TOKEN",
              value: apifyToken,
            },
          ],
        },
      ],
    },
  },
});

// Permitir acceso público al Backend
const backendIam = new gcp.cloudrun.IamMember("backendIam", {
  service: backendService.name,
  location: backendService.location,
  role: "roles/run.invoker",
  member: "allUsers",
});

// Crear servicio de Cloud Run para el Frontend usando la imagen construida
const frontendService = new gcp.cloudrun.Service("frontendService", {
  location: region,
  template: {
    spec: {
      containers: [
        {
          image: frontendImage.imageName,
          ports: [{ containerPort: 8501 }],
          envs: [
            {
              name: "BACKEND_URL",
              value: backendUrl,
            },
          ],
        },
      ],
    },
  },
});

// Permitir acceso público al Frontend
const frontendIam = new gcp.cloudrun.IamMember("frontendIam", {
  service: frontendService.name,
  location: frontendService.location,
  role: "roles/run.invoker",
  member: "allUsers",
});

// Exportar las URLs de los servicios
export const backendServiceUrl = backendService.statuses.apply(
  (statuses) => statuses?.[0]?.url
);
export const frontendServiceUrl = frontendService.statuses.apply(
  (statuses) => statuses?.[0]?.url
);
