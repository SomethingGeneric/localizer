test:
	python3 app.py
pip:
	sudo pip3 install -r requirements.txt
deploy: pip
	cp sample.service new.service
	# yes, this exists because I'm too lazy to escape regex + inline 'sed'
	python3 sed.py
	sudo mv new.service /etc/systemd/system/localizer.service
	sudo systemctl daemon-reload
	sudo systemctl enable --now localizer.service
undeploy:
	sudo systemctl stop localizer.service
	sudo systemctl disable localizer.service
	sudo rm /etc/systemd/system/localizer.service
	sudo systemctl daemon-reload
update:
	make undeploy
	git pull
	make deploy
