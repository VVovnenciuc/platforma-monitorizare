#==============  Provider  ==============

provider "aws" {
  region                      = "eu-central-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  s3_force_path_style         = true

  endpoints {
    ec2 = "http://localhost:4566"
    s3  = "http://localhost:4566"
    iam = "http://localhost:4566"
  }
}

#==============  Resurse  ==============

# S3 bucket
resource "aws_s3_bucket" "project_bucket" {
  bucket = "tf-project-bucket"
}

# Key Pair (cheie SSH locală), ~/.ssh/id_rsa.pub trebuie sa existe
resource "aws_key_pair" "deploy_key" {
  key_name   = "local-dev-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

# EC2 Instance (în LocalStack)
resource "aws_instance" "app" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  key_name      = aws_key_pair.deploy_key.key_name
}

#==============  Output  ==============

output "ec2_instance_id" {
  value = aws_instance.app.id
}
