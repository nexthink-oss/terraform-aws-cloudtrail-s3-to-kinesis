resource "aws_lambda_permission" "cloudtrail-sns-to-lambda" {
  statement_id  = "AllowExecutionFromSnsTopic"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda-cloudtrail.arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.cloudtrail.arn
}

resource "aws_sns_topic_subscription" "cloudtrail-sns-to-lambda" {
  topic_arn = aws_sns_topic.cloudtrail.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.lambda-cloudtrail.arn

  depends_on = [aws_lambda_permission.cloudtrail-sns-to-lambda]
}
