# No projeto, em infra/backend.tf, para o pipeline do GitHub Actions: o estado fica num bucket S3,
# com um caminho por workspace (env:/<workspace>/<key>). A credencial vem da identidade federada.
terraform {
  backend "s3" {
    bucket       = "estado-iac-exemplo"
    key          = "servicos/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
