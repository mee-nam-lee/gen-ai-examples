"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.StatusCode = exports.ResponseMode = exports.LookerAppId = void 0;
exports.addQueryParams = addQueryParams;
exports.defaultTimeout = exports.contentPatternString = exports.contentPatternBinary = exports.charsetUtf8Pattern = exports.agentPrefix = void 0;
exports.encodeParam = encodeParam;
exports.encodeParams = encodeParams;
exports.isErrorLike = isErrorLike;
exports.isUtf8 = isUtf8;
exports.responseMode = responseMode;
exports.safeBase64 = safeBase64;
exports.sdkError = sdkError;
exports.sdkOk = sdkOk;
exports.trace = trace;
var _constants = require("./constants");
var _delimArray = require("./delimArray");
var _lookerSDKError = require("./lookerSDKError");
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }
function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }
var agentPrefix = 'TS-SDK';
exports.agentPrefix = agentPrefix;
var LookerAppId = 'x-looker-appid';
exports.LookerAppId = LookerAppId;
var tracing = false;
function trace(message, info) {
  if (tracing) {
    console.debug(message);
    if (info) {
      console.debug({
        info
      });
    }
  }
}
var ResponseMode = function (ResponseMode) {
  ResponseMode[ResponseMode["binary"] = 0] = "binary";
  ResponseMode[ResponseMode["string"] = 1] = "string";
  ResponseMode[ResponseMode["unknown"] = 2] = "unknown";
  return ResponseMode;
}({});
exports.ResponseMode = ResponseMode;
var contentPatternString = new RegExp(_constants.matchModeString, 'i');
exports.contentPatternString = contentPatternString;
var contentPatternBinary = new RegExp(_constants.matchModeBinary, 'i');
exports.contentPatternBinary = contentPatternBinary;
var charsetUtf8Pattern = new RegExp(_constants.matchCharsetUtf8, 'i');
exports.charsetUtf8Pattern = charsetUtf8Pattern;
var defaultTimeout = 120;
exports.defaultTimeout = defaultTimeout;
var StatusCode = function (StatusCode) {
  StatusCode[StatusCode["OK"] = 200] = "OK";
  StatusCode[StatusCode["Created"] = 201] = "Created";
  StatusCode[StatusCode["Accepted"] = 202] = "Accepted";
  StatusCode[StatusCode["NonAuthoritative"] = 203] = "NonAuthoritative";
  StatusCode[StatusCode["NoContent"] = 204] = "NoContent";
  StatusCode[StatusCode["ResetContent"] = 205] = "ResetContent";
  StatusCode[StatusCode["PartialContent"] = 206] = "PartialContent";
  StatusCode[StatusCode["MultiStatus"] = 207] = "MultiStatus";
  StatusCode[StatusCode["MultiStatusDav"] = 208] = "MultiStatusDav";
  StatusCode[StatusCode["IMUsed"] = 226] = "IMUsed";
  StatusCode[StatusCode["MultipleChoice"] = 300] = "MultipleChoice";
  StatusCode[StatusCode["MovedPermanently"] = 301] = "MovedPermanently";
  StatusCode[StatusCode["Found"] = 302] = "Found";
  StatusCode[StatusCode["SeeOther"] = 303] = "SeeOther";
  StatusCode[StatusCode["NotModified"] = 304] = "NotModified";
  StatusCode[StatusCode["UseProxy"] = 305] = "UseProxy";
  StatusCode[StatusCode["UnusedRedirect"] = 306] = "UnusedRedirect";
  StatusCode[StatusCode["TemporaryRedirect"] = 307] = "TemporaryRedirect";
  StatusCode[StatusCode["PermanentRedirect"] = 308] = "PermanentRedirect";
  StatusCode[StatusCode["BadRequest"] = 400] = "BadRequest";
  StatusCode[StatusCode["Unauthorized"] = 401] = "Unauthorized";
  StatusCode[StatusCode["PaymentRequired"] = 402] = "PaymentRequired";
  StatusCode[StatusCode["Forbidden"] = 403] = "Forbidden";
  StatusCode[StatusCode["NotFound"] = 404] = "NotFound";
  StatusCode[StatusCode["MethodNotAllowed"] = 405] = "MethodNotAllowed";
  StatusCode[StatusCode["NotAcceptable"] = 406] = "NotAcceptable";
  StatusCode[StatusCode["ProxyAuthRequired"] = 407] = "ProxyAuthRequired";
  StatusCode[StatusCode["RequestTimeout"] = 408] = "RequestTimeout";
  StatusCode[StatusCode["Conflict"] = 409] = "Conflict";
  StatusCode[StatusCode["Gone"] = 410] = "Gone";
  StatusCode[StatusCode["LengthRequired"] = 411] = "LengthRequired";
  StatusCode[StatusCode["PreconditionFailed"] = 412] = "PreconditionFailed";
  StatusCode[StatusCode["PayloadTooLarge"] = 413] = "PayloadTooLarge";
  StatusCode[StatusCode["UriTooLong"] = 414] = "UriTooLong";
  StatusCode[StatusCode["UnsupportedMediaType"] = 415] = "UnsupportedMediaType";
  StatusCode[StatusCode["RequestedRangeNotSatisfiable"] = 416] = "RequestedRangeNotSatisfiable";
  StatusCode[StatusCode["ExpectationFailed"] = 417] = "ExpectationFailed";
  StatusCode[StatusCode["ImATeapot"] = 418] = "ImATeapot";
  StatusCode[StatusCode["MisdirectedRequest"] = 421] = "MisdirectedRequest";
  StatusCode[StatusCode["UnprocessableEntity"] = 422] = "UnprocessableEntity";
  StatusCode[StatusCode["Locked"] = 423] = "Locked";
  StatusCode[StatusCode["FailedDependency"] = 424] = "FailedDependency";
  StatusCode[StatusCode["TooEarly"] = 425] = "TooEarly";
  StatusCode[StatusCode["UpgradeRequired"] = 426] = "UpgradeRequired";
  StatusCode[StatusCode["PreconditionRequired"] = 428] = "PreconditionRequired";
  StatusCode[StatusCode["TooManyRequests"] = 429] = "TooManyRequests";
  StatusCode[StatusCode["RequestHeaderFieldsTooLarge"] = 431] = "RequestHeaderFieldsTooLarge";
  StatusCode[StatusCode["UnavailableForLegalReasons"] = 451] = "UnavailableForLegalReasons";
  StatusCode[StatusCode["InternalServerError"] = 500] = "InternalServerError";
  StatusCode[StatusCode["NotImplemented"] = 501] = "NotImplemented";
  StatusCode[StatusCode["BadGateway"] = 502] = "BadGateway";
  StatusCode[StatusCode["ServiceUnavailable"] = 503] = "ServiceUnavailable";
  StatusCode[StatusCode["GatewayTimeout"] = 504] = "GatewayTimeout";
  StatusCode[StatusCode["HttpVersionNotSupported"] = 505] = "HttpVersionNotSupported";
  StatusCode[StatusCode["VariantAlsoNegotiates"] = 506] = "VariantAlsoNegotiates";
  StatusCode[StatusCode["InsufficientStorage"] = 507] = "InsufficientStorage";
  StatusCode[StatusCode["LoopDetected"] = 508] = "LoopDetected";
  StatusCode[StatusCode["NotExtended"] = 510] = "NotExtended";
  StatusCode[StatusCode["NetworkAuthRequired"] = 511] = "NetworkAuthRequired";
  return StatusCode;
}({});
exports.StatusCode = StatusCode;
function responseMode(contentType) {
  if (contentType.match(contentPatternString)) {
    return ResponseMode.string;
  }
  if (contentType.match(contentPatternBinary)) {
    return ResponseMode.binary;
  }
  return ResponseMode.unknown;
}
function isUtf8(contentType) {
  return contentType.match(/;.*\bcharset\b=\butf-8\b/i);
}
function encodeParam(value) {
  if (value instanceof Date) {
    value = value.toISOString();
  } else if (value instanceof _delimArray.DelimArray) {
    value = value.toString();
  }
  var encoded = typeof value === 'object' ? JSON.stringify(value) : value.toString();
  try {
    var decoded = decodeURIComponent(value);
    if (value === decoded) {
      encoded = encodeURIComponent(value);
    }
  } catch (e) {
    if (e instanceof URIError) {
      encoded = encodeURIComponent(value);
    } else {
      throw e;
    }
  }
  return encoded;
}
function encodeParams(values) {
  if (!values) return '';
  var keys = Object.keys(values);
  return keys.filter(k => values[k] !== undefined).map(k => k + '=' + encodeParam(values[k])).join('&');
}
function addQueryParams(path, obj) {
  if (!obj) {
    return path;
  }
  var qp = encodeParams(obj);
  return "".concat(path).concat(qp ? '?' + qp : '');
}
var utf8 = 'utf-8';
function bufferString(val) {
  var result = 'Unknown error';
  try {
    var decoder = new TextDecoder(utf8);
    result = decoder.decode(val);
  } catch (e) {
    try {
      if (val instanceof Buffer) {
        result = Buffer.from(val).toString(utf8);
      } else {
        result = JSON.stringify(val);
      }
    } catch (err) {
      result = JSON.stringify(val);
    }
  }
  return result;
}
function sdkError(response) {
  if (typeof response === 'string') {
    return new _lookerSDKError.LookerSDKError(response);
  }
  if ('error' in response) {
    var _error = response.error;
    if (typeof _error === 'string') {
      return new _lookerSDKError.LookerSDKError(_error);
    }
    if ('error' in _error) {
      var _result = bufferString(_error.error);
      return new _lookerSDKError.LookerSDKError(_result);
    }
    if ('message' in _error) {
      return new _lookerSDKError.LookerSDKError(response.error.message.toString(), {
        errors: _error.errors,
        documentation_url: _error.documentation_url
      });
    }
    if ('statusMessage' in _error) {
      return new _lookerSDKError.LookerSDKError(_error.statusMessage);
    }
    var result = bufferString(_error);
    return new _lookerSDKError.LookerSDKError(result);
  }
  if ('message' in response) {
    return new _lookerSDKError.LookerSDKError(response.message);
  }
  var error = JSON.stringify(response);
  return new _lookerSDKError.LookerSDKError("Unknown error with SDK method ".concat(error));
}
function sdkOk(_x) {
  return _sdkOk.apply(this, arguments);
}
function _sdkOk() {
  _sdkOk = _asyncToGenerator(function* (promise) {
    var result = yield promise;
    if (result.ok) {
      return result.value;
    } else {
      throw sdkError(result);
    }
  });
  return _sdkOk.apply(this, arguments);
}
function safeBase64(u8) {
  var rawBase64 = btoa(String.fromCharCode(...u8));
  return rawBase64.replace(/\+/g, '-').replace(/\//g, '_');
}
function isErrorLike(error) {
  if (typeof error !== 'object') return false;
  if (!error) return false;
  if (!Object.prototype.hasOwnProperty.call(error, 'message')) return false;
  if (typeof error.message !== 'string') return false;
  return true;
}
//# sourceMappingURL=transport.js.map