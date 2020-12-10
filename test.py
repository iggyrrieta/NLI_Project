from dm_core.main import DMCore
import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)


if __name__ == "__main__":
    DMCore().start()