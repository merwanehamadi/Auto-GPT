# List of files to download
files=("docker-compose.yml" ".env.template" "prompt_settings.yaml" "azure.yaml.template")

# Download each file in the list
for file in "${files[@]}"
do
  sudo curl -L "https://github.com/merwanehamadi/Auto-GPT/raw/install-branch/tools/$file" -o "$file"
done

# Create an additional file
touch ai_settings.yaml

echo "The following files have been added:"
for file in "${files[@]}"
do
  echo "- $file"
done
