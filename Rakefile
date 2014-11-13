FILENAME = 'google_appengine_1.9.15.zip'
SDK_SRC = "https://storage.googleapis.com/appengine-sdks/featured/#{FILENAME}"
CLOUDBEES_SRC = '/opt/google/gae_python_sdk/1.8.latest/'
VERBOSE = true

def execute_command(command)
  puts(command)
  system(command)

  $?.exitstatus
end

file 'venv/bin/activate' do
  execute_command('virtualenv venv') unless Dir.exists?('venv')
end

file 'google_appengine' do
  if Dir.exists?(CLOUDBEES_SRC)
    FileUtils.ln_s(CLOUDBEES_SRC, 'google_appengine', :verbose => VERBOSE)
  else
    execute_command("wget #{SDK_SRC} -nv || curl -O #{SDK_SRC}")
    execute_command("unzip -q #{FILENAME}")
  end
end

task :all => [:clean, :test] do
end

task :clean do
  execute_command('find . -name "*.pyc" -exec rm -rf {} \;')
  FileUtils.rm_rf('venv', :verbose => VERBOSE) if Dir.exists?('venv')

  if File.symlink?('google_appengine')
    FileUtils.rm('google_appengine')
  elsif Dir.exists?('google_appengine')
    FileUtils.rm_rf('google_appengine')
  end

  FileUtils.rm("#{FILENAME}", :verbose => VERBOSE) if File.exists?("#{FILENAME}")
end

task :venv => ['requirements.txt', 'venv/bin/activate'] do
  execute_command('. venv/bin/activate; pip install -Ur requirements.txt')
  FileUtils.touch('venv/bin/activate', :verbose => VERBOSE)
end

task :test => [:venv] do
  execute_command('. venv/bin/activate; PYTHONPATH="." ./tests/RunTests.py')
end

task :build => [:venv, 'google_appengine'] do
  execute_command('. venv/bin/activate; PYTHONPATH=./tests/ nosetests --with-xunit --with-coverage --cover-html --cover-erase --with-gae --gae-lib-root=google_appengine ./tests/func/ ./tests/unit/ ./tests/test_lib/')
end
