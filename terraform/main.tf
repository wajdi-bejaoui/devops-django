provider "kubernetes" {
  config_path = "C:\\Users\\wajdi\\.kube\\config"

}



resource "kubernetes_manifest" "django_deployment" {
  manifest = {
    apiVersion = "apps/v1"
    kind       = "Deployment"
    metadata = {
      name      = "django-app"
      namespace = "default"
    }
    spec = {
      replicas = 1
      selector = {
        matchLabels = {
          app = "django-app"
        }
      }
      template = {
        metadata = {
          labels = {
            app = "django-app"
          }
        }
        spec = {
          containers = [
            {
              name  = "django-app"
              image = "wajdibejaoui/django_test:latest"
              ports = [
                {
                  containerPort = 8000
                }
              ]
              env = [
                {
                  name = "DJANGO_SETTINGS_MODULE"
                  valueFrom = {
                    configMapKeyRef = {
                      name = "django-config"
                      key  = "DJANGO_SETTINGS_MODULE"
                    }
                  }
                },
                {
                  name = "DATABASE_HOST"
                  valueFrom = {
                    configMapKeyRef = {
                      name = "django-config"
                      key  = "DATABASE_HOST"
                    }
                  }
                },
                {
                  name = "DATABASE_PORT"
                  valueFrom = {
                    configMapKeyRef = {
                      name = "django-config"
                      key  = "DATABASE_PORT"
                    }
                  }
                },
                {
                  name = "MYSQL_DATABASE"
                  valueFrom = {
                    configMapKeyRef = {
                      name = "django-config"
                      key  = "MYSQL_DATABASE"
                    }
                  }
                },
                {
                  name = "MYSQL_USER"
                  valueFrom = {
                    secretKeyRef = {
                      name = "mysql-secret"
                      key  = "MYSQL_USER"
                    }
                  }
                },
                {
                  name = "MYSQL_PASSWORD"
                  valueFrom = {
                    secretKeyRef = {
                      name = "mysql-secret"
                      key  = "MYSQL_PASSWORD"
                    }
                  }
                }
              ]
              volumeMounts = [
                {
                  name      = "static-files"
                  mountPath = "/app/static"
                }
              ]
            }
          ]
          volumes = [
            {
              name = "static-files"
              emptyDir = {}
            }
          ]
        }
      }
    }
  }
}

resource "kubernetes_manifest" "django_service" {
  manifest = {
    apiVersion = "v1"
    kind       = "Service"
    metadata = {
      name      = "django-service"
      namespace = "default"
    }
    spec = {
      ports = [
        {
          port       = 8000
          targetPort = 8000
        }
      ]
      selector = {
        app = "django-app"
      }
      type = "NodePort"
    }
  }
}

resource "kubernetes_manifest" "mysql_deployment" {
  manifest = {
    apiVersion = "apps/v1"
    kind       = "Deployment"
    metadata = {
      name      = "mysql"
      namespace = "default"
    }
    spec = {
      replicas = 1
      selector = {
        matchLabels = {
          app = "mysql"
        }
      }
      template = {
        metadata = {
          labels = {
            app = "mysql"
          }
        }
        spec = {
          containers = [
            {
              name  = "mysql"
              image = "mysql:8.0"
              ports = [
                {
                  containerPort = 3306
                }
              ]
              env = [
                {
                  name = "MYSQL_DATABASE"
                  valueFrom = {
                    configMapKeyRef = {
                      name = "django-config"
                      key  = "MYSQL_DATABASE"
                    }
                  }
                },
                {
                  name = "MYSQL_USER"
                  valueFrom = {
                    secretKeyRef = {
                      name = "mysql-secret"
                      key  = "MYSQL_USER"
                    }
                  }
                },
                {
                  name = "MYSQL_PASSWORD"
                  valueFrom = {
                    secretKeyRef = {
                      name = "mysql-secret"
                      key  = "MYSQL_PASSWORD"
                    }
                  }
                },
                {
                  name = "MYSQL_ROOT_PASSWORD"
                  valueFrom = {
                    secretKeyRef = {
                      name = "mysql-secret"
                      key  = "MYSQL_ROOT_PASSWORD"
                    }
                  }
                }
              ]
              volumeMounts = [
                {
                  name      = "mysql-persistent-storage"
                  mountPath = "/var/lib/mysql"
                }
              ]
            }
          ]
          volumes = [
            {
              name = "mysql-persistent-storage"
              persistentVolumeClaim = {
                claimName = "mysql-pvc"
              }
            }
          ]
        }
      }
    }
  }
}

resource "kubernetes_manifest" "mysql_pvc" {
  manifest = {
    apiVersion = "v1"
    kind       = "PersistentVolumeClaim"
    metadata = {
      name      = "mysql-pvc"
      namespace = "default"
    }
    spec = {
      accessModes = ["ReadWriteOnce"]
      resources = {
        requests = {
          storage = "10Gi"
        }
      }
    }
  }
}

resource "kubernetes_manifest" "mysql_service" {
  manifest = {
    apiVersion = "v1"
    kind       = "Service"
    metadata = {
      name      = "mysql"
      namespace = "default"
    }
    spec = {
      ports = [
        {
          port       = 3306
          targetPort = 3306
        }
      ]
      selector = {
        app = "mysql"
      }
    }
  }
}

resource "kubernetes_manifest" "django_config" {
  manifest = {
    apiVersion = "v1"
    kind       = "ConfigMap"
    metadata = {
      name      = "django-config"
      namespace = "default"
    }
    data = {
      DJANGO_SETTINGS_MODULE = "auth.settings"
      DATABASE_HOST         = "mysql"
      DATABASE_PORT         = "3306"
      MYSQL_DATABASE       = "django_db"
    }
  }
}

resource "kubernetes_manifest" "mysql_secret" {
  manifest = {
    apiVersion = "v1"
    kind       = "Secret"
    metadata = {
      name      = "mysql-secret"
      namespace = "default"
    }
    type = "Opaque"
    data = {
      MYSQL_USER          = "dGVzdA=="
      MYSQL_PASSWORD      = "dGVzdA=="
      MYSQL_ROOT_PASSWORD = "dGVzdA=="
    }
  }
}