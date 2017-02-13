class ConfigInfo(object):
    def __init__(self, conf_file_path):
        self.load_config(conf_file_path)

    def load_config(self, conf_file_path):
        """Load config from config file
        """