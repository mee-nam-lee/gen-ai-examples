"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.LookerSDKError = void 0;
var _excluded = ["errors", "documentation_url"];
function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }
function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; var sourceKeys = Object.keys(source); var key, i; for (i = 0; i < sourceKeys.length; i++) { key = sourceKeys[i]; if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } return target; }
var LookerSDKError = (() => {
  'use strict';

  var LookerSDKErrorConstructor = function LookerSDKError() {
    var _errors, _documentation_url;
    for (var _len = arguments.length, _ref = new Array(_len), _key = 0; _key < _len; _key++) {
      _ref[_key] = arguments[_key];
    }
    var [message, _ref2 = {}, ...rest] = _ref;
    var {
        errors,
        documentation_url
      } = _ref2,
      errorOptions = _objectWithoutProperties(_ref2, _excluded);
    (_errors = errors) !== null && _errors !== void 0 ? _errors : errors = [];
    (_documentation_url = documentation_url) !== null && _documentation_url !== void 0 ? _documentation_url : documentation_url = '';
    var error = this ? new Error(message, errorOptions, ...rest) : Error(message, errorOptions, ...rest);
    Object.setPrototypeOf(error, this ? Object.getPrototypeOf(this) : LookerSDKError.prototype);
    Object.defineProperty(error, 'message', {
      enumerable: true
    });
    error.errors = errors;
    error.documentation_url = documentation_url;
    return error;
  };
  Object.defineProperty(LookerSDKErrorConstructor, 'prototype', {
    value: Object.create(Error.prototype, {
      constructor: {
        value: LookerSDKErrorConstructor,
        writable: true,
        configurable: true
      },
      name: {
        value: 'LookerSDKError',
        writable: true,
        configurable: true
      }
    }),
    writable: false
  });
  return LookerSDKErrorConstructor;
})();
exports.LookerSDKError = LookerSDKError;
//# sourceMappingURL=lookerSDKError.js.map