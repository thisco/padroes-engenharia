terraform {
  required_providers {
    local = { source = "hashicorp/local", version = "~> 2.5" }
  }
}

variable "replicas" { type = number }

# O serviço do ambiente: some com o destroy.
resource "local_file" "servico" {
  filename = "${path.module}/saida/${terraform.workspace}/servico.txt"
  content  = "replicas=${var.replicas}\n"
}

# O banco do ambiente: caro de recriar, protegido contra destroy. Tirar a proteção é uma MR revisada.
resource "local_file" "banco" {
  filename = "${path.module}/saida/${terraform.workspace}/banco.txt"
  content  = "dados\n"
  lifecycle {
    prevent_destroy = true
  }
}
