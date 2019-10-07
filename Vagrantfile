Vagrant.configure('2') do |config|
	config.vm.box = 'ubuntu/disco64'

	config.vm.provision 'file', source: './twitter-dl.py', destination: '$HOME/twitter-dl.py'
	config.vm.provision 'file', source: './requirements.txt', destination: '$HOME/requirements.txt'
	config.vm.define 'twitter-dl'
	config.vm.hostname = 'twitter-dl'
	config.vm.provision 'shell',
		inline: 'sudo apt update && sudo apt install -y python3-pip ffmpeg && pip3 install -r requirements.txt'
	config.vm.network 'forwarded_port', guest: 8000, host: 8000,
		auto_correct: true
end
