# type: ignore
import src.hashers.hashlib as hashlib
import src.hashers.dhash as dhash
import src.hashers.perception as perception

enabled_hashers = {
    'dhash.dhash': dhash.dhash,
    'perception.AverageHash': perception.AverageHash,
    'perception.PHash': perception.PHash,
    'perception.WaveletHash': perception.WaveletHash,
    'perception.MarrHildreth': perception.MarrHildreth,
    'perception.BlockMean': perception.BlockMean,
    'perception.DHash': perception.DHash,
    'hashlib.md5': hashlib.md5,
}