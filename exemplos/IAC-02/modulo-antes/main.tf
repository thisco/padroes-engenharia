terraform {
  required_version = ">= 1.6"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

variable "ambiente" {
  type    = string
  default = "dev"
}

resource "local_file" "config" {
  filename = "${path.module}/saida/app-${var.ambiente}.txt"
  content  = "ambiente=${var.ambiente}\n"
}
