provider "aws" {
  region = "eu-north-1"
}

resource "aws_security_group" "ec2_sg" {
  name_prefix = "ec2-sg"
  description = "Allow HTTP and SSH inbound traffic"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" { 
  ami           = "ami-09a9858973b288bdd" 
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  
  tags = {
    Name = "EC2-Web-Instance"
  }
}
resource "aws_launch_template" "web_template" {
  name = "web-launch-template"
  image_id = "ami-09a9858973b288bdd"  # Replace with your AMI ID
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  
}

resource "aws_autoscaling_group" "web_asg" {
  desired_capacity = 1
  max_size = 3
  min_size = 1
  vpc_zone_identifier = ["subnet-0ac83edbd029f5644"]  # Your subnet ID
  health_check_type = "EC2"
  health_check_grace_period = 300
launch_template {
       name   = aws_launch_template.web_template.name
      version   = "$Latest"
}

 }
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name = "High-CPU-Alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = "2"
  metric_name = "CPUUtilization"
  namespace = "AWS/EC2"
  period = "300"
  statistic = "Average"
  threshold = "0.1"
  alarm_description = "Triggered when CPU utilization exceeds 0.1%."
  insufficient_data_actions = []
}

