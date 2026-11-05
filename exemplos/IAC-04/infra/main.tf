terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

# Os valores que mudam por ambiente: um arquivo por ambiente em ambientes/.
variable "replicas" {
  type = number
}

# A versão de todos os serviços: a mesma tag, vinda do pipeline (TF_VAR_versao).
variable "versao" {
  type = string
}

# Um arquivo por serviço faz o papel do recurso de nuvem: o estado fica no workspace.
resource "local_file" "servico" {
  for_each = toset(["api", "worker"])
  filename = "${path.module}/saida/${terraform.workspace}/${each.key}.txt"
  content  = "imagem=registro.exemplo/${each.key}:${var.versao}\nreplicas=${var.replicas}\n"
}
