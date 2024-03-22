export declare namespace env {
    const browser: boolean;
    const jest: boolean;
    const node: boolean;
}
declare const _extends: string[];
export { _extends as extends };
export declare const ignorePatterns: string[];
export declare const overrides: ({
    extends: string[];
    files: string[];
    rules: {
        'header/header': string;
        'import/no-extraneous-dependencies': string;
        'react/jsx-no-undef': string;
        'i18next/no-literal-string'?: undefined;
        '@typescript-eslint/no-var-requires'?: undefined;
        '@looker/no-private-dependencies'?: undefined;
        'no-unused-expressions'?: undefined;
        'sort-keys-fix/sort-keys-fix'?: undefined;
    };
} | {
    files: string[];
    rules: {
        'i18next/no-literal-string': string;
        'header/header'?: undefined;
        'import/no-extraneous-dependencies'?: undefined;
        'react/jsx-no-undef'?: undefined;
        '@typescript-eslint/no-var-requires'?: undefined;
        '@looker/no-private-dependencies'?: undefined;
        'no-unused-expressions'?: undefined;
        'sort-keys-fix/sort-keys-fix'?: undefined;
    };
    extends?: undefined;
} | {
    files: string[];
    rules: {
        '@typescript-eslint/no-var-requires': string;
        'header/header'?: undefined;
        'import/no-extraneous-dependencies'?: undefined;
        'react/jsx-no-undef'?: undefined;
        'i18next/no-literal-string'?: undefined;
        '@looker/no-private-dependencies'?: undefined;
        'no-unused-expressions'?: undefined;
        'sort-keys-fix/sort-keys-fix'?: undefined;
    };
    extends?: undefined;
} | {
    extends: string[];
    files: string[];
    rules: {
        '@looker/no-private-dependencies': (string | {
            exclude: string[];
        })[];
        'header/header': string;
        'no-unused-expressions': string;
        'sort-keys-fix/sort-keys-fix': string;
        'import/no-extraneous-dependencies'?: undefined;
        'react/jsx-no-undef'?: undefined;
        'i18next/no-literal-string'?: undefined;
        '@typescript-eslint/no-var-requires'?: undefined;
    };
})[];
export declare const parser: string;
export declare const plugins: string[];
export declare const rules: {
    '@typescript-eslint/consistent-type-imports': string;
    '@typescript-eslint/explicit-function-return-type': string;
    '@typescript-eslint/explicit-module-boundary-types': string;
    '@typescript-eslint/no-redeclare': string[];
    '@typescript-eslint/no-unused-vars': string;
    '@typescript-eslint/no-use-before-define': string;
    'header/header': (string | number | (string | {
        pattern: string;
        template: string;
    })[])[];
    'import/default': string;
    'import/named': string;
    'import/no-extraneous-dependencies': string;
    'import/order': string;
    indentation: string;
    'lodash/import-scope': string[];
    'no-console': string;
    'no-nested-ternary': string;
    'no-redeclare': string;
    'no-restricted-imports': (string | {
        patterns: string[];
    })[];
    'no-restricted-properties': (number | {
        message: string;
        property: string;
    })[];
    'no-use-before-define': string;
    'react/display-name': string;
    'react/no-unescaped-entities': string;
    'react/prop-types': string;
    'sort-keys': string;
    'sort-keys-fix/sort-keys-fix': string;
    'testing-library/no-node-access': string;
};
export declare namespace settings {
    namespace react {
        const version: string;
    }
}
