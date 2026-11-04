# No projeto, em infra/backend.tf, para o pipeline do GitLab: o estado fica no GitLab. O endereço
# (um estado por ambiente) e a credencial vêm das variáveis TF_HTTP_* do job.
terraform {
  backend "http" {}
}
