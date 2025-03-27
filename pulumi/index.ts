import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";
import * as gcp from "@pulumi/gcp";
import * as dotenv from "dotenv";

dotenv.config();

// Obtener variables de entorno
const project = process.env.GCP_PROJECT_ID;
const region = process.env.GCP_REGION;
const zone = process.env.GCP_ZONE;

if (!project || !region || !zone) {
  throw new Error(
    "Missing required environment variables: GCP_PROJECT_ID, GCP_REGION, or GCP_ZONE"
  );
}

// Configurar el proveedor de GCP con las credenciales del service account
const gcpProvider = new gcp.Provider("gcp-provider", {
  credentials: process.env.GCP_SERVICE_ACCOUNT_KEY,
  project: project,
  region: region,
  zone: zone,
});

// Obtener variables de entorno desde la configuración de Pulumi
const apifyToken = process.env.APIFY_API_TOKEN;
const backendUrl = process.env.BACKEND_URL;

// Crear el repositorio de Artifact Registry
const repository = new gcp.artifactregistry.Repository(
  "frontend-repo",
  {
    location: region,
    repositoryId: "frontend-repo",
    description: "Docker repository for frontend images",
    format: "DOCKER",
  },
  { provider: gcpProvider }
);

// Configuración del registro (usando Artifact Registry)
const registryInfo = {
  server: `${region}-docker.pkg.dev`,
  username: "_json_key",
  // La contraseña es la clave JSON en formato string
  password: process.env.GCP_SERVICE_ACCOUNT_KEY,
};

// Construir y subir la imagen del Frontend
const frontendImage = new docker.Image("frontendImage", {
  build: {
    context: "..",
    dockerfile: "..\\frontend\\Dockerfile",
  },
  imageName: pulumi.interpolate`${region}-docker.pkg.dev/${project}/frontend-repo/frontend:latest`,
  registry: registryInfo,
});

// Crear servicio de Cloud Run para el Frontend usando la imagen construida
const frontendService = new gcp.cloudrun.Service(
  "frontendService",
  {
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
              {
                name: "APIFY_TOKEN",
                value: apifyToken,
              },
            ],
          },
        ],
      },
    },
  },
  { provider: gcpProvider }
);

// Permitir acceso público al Frontend
const frontendIam = new gcp.cloudrun.IamMember(
  "frontendIam",
  {
    service: frontendService.name,
    location: frontendService.location,
    role: "roles/run.invoker",
    member: "allUsers",
  },
  { provider: gcpProvider }
);

// Exportar las URLs de los servicios
export const frontendServiceUrl = frontendService.statuses.apply(
  (statuses) => statuses?.[0]?.url
);
