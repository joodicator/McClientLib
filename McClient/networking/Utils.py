import array
import string
from hashlib import sha1


def generate_serverID(serverID, secret, pubkey):
    hasher = sha1()
    hasher.update(serverID)
    hasher.update(secret)
    hasher.update(pubkey)

    return java_digest(hasher)


# This function courtesy of barneygale
def java_digest(digest):
    d = long(digest.hexdigest(), 16)
    if d >> 39 * 4 & 0x8:
        d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
    else:
        d = "%x" % d
    return d


def hex2str(hex_num):
    return ''.join(["%02X " % ord(x) for x in hex_num]).strip()


def stringToByteArray(string):
    return array.array('B', string.decode("hex"))


def TwosCompliment(digest):
    carry = True
    for i in range((digest.__len__() - 1), -1, -1):
        value = 255 - digest[i]
        digest[i] = value
        if(carry):
            carry = digest[i] == 0xFF
            digest[i] = digest[i] + 1
    return digest


def trimStart(string, character):
    for c in string:
        if (c == character):
            string = string[1:]
        else:
            break
    return string


def getHexString(byteArray):
    result = ""
    for i in range(byteArray.__len__()):
        if (byteArray[i] < 0x10):
            result += '0'
        result += hex(byteArray[i])[2:]
    return result


def unpackNbt(tag):
    """Unpack an NBT tag into a native Python data structure."""
    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value


def packNbt(s):
    """
    Pack a native Python data structure into an NBT tag. Only the following
    structures and types are supported:

     * int
     * float
     * str
     * unicode
     * dict

    Additionally, arbitrary iterables are supported.

    Packing is not lossless. In order to avoid data loss, TAG_Long and
    TAG_Double are preferred over the less precise numerical formats.

    Lists and tuples may become dicts on unpacking if they were not homogenous
    during packing, as a side-effect of NBT's format. Nothing can be done
    about this.

    Only strings are supported as keys for dicts and other mapping types. If
    your keys are not strings, they will be coerced. (Resistance is futile.)
    """

    if isinstance(s, int):
        return TAG_Long(s)
    elif isinstance(s, float):
        return TAG_Double(s)
    elif isinstance(s, (str, unicode)):
        return TAG_String(s)
    elif isinstance(s, dict):
        tag = TAG_Compound()
        for k, v in s:
            v = pack_nbt(v)
            v.name = str(k)
            tag.tags.append(v)
        return tag
    elif hasattr(s, "__iter__"):
        # We arrive at a slight quandry. NBT lists must be homogenous, unlike
        # Python lists. NBT compounds work, but require unique names for every
        # entry. On the plus side, this technique should work for arbitrary
        # iterables as well.
        tags = [pack_nbt(i) for i in s]
        t = type(tags[0])
        # If we're homogenous...
        if all(t == type(i) for i in tags):
            tag = TAG_List(type=t)
            tag.tags = tags
        else:
            tag = TAG_Compound()
            for i, item in enumerate(tags):
                item.name = str(i)
            tag.tags = tags
        return tag
    else:
        raise ValueError("Couldn't serialise type %s!" % type(s))