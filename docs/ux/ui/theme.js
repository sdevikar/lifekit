// React Theme — extracted from https://platform.claude.com/docs/en/home
// Compatible with: Chakra UI, Stitches, Vanilla Extract, or any CSS-in-JS

/**
 * TypeScript type definition for this theme:
 *
 * interface Theme {
 *   colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    foreground: string;
    neutral50: string;
    neutral100: string;
    neutral200: string;
    neutral300: string;
    neutral400: string;
    neutral500: string;
    neutral600: string;
 *   };
 *   fonts: {
    body: string;
    mono: string;
 *   };
 *   fontSizes: {
    '12': string;
    '13': string;
    '14': string;
    '15': string;
    '16': string;
    '18': string;
    '20': string;
    '22': string;
    '24': string;
    '26': string;
    '52': string;
 *   };
 *   space: {
    '1': string;
    '20': string;
    '24': string;
    '28': string;
    '41': string;
    '46': string;
    '56': string;
    '64': string;
    '78': string;
    '89': string;
    '103': string;
    '115': string;
    '128': string;
    '139': string;
    '148': string;
    '164': string;
 *   };
 *   radii: {
    sm: string;
    md: string;
    lg: string;
 *   };
 *   shadows: {
    none: string;
    xs: string;
    lg: string;
    xl: string;
 *   };
 *   states: {
 *     hover: { opacity: number };
 *     focus: { opacity: number };
 *     active: { opacity: number };
 *     disabled: { opacity: number };
 *   };
 * }
 */

export const theme = {
  "colors": {
    "primary": "#cf222e",
    "secondary": "#0550ae",
    "accent": "#6da7ec",
    "background": "#fcfcfb",
    "foreground": "#0b0b0b",
    "neutral50": "#0b0b0b",
    "neutral100": "#898781",
    "neutral200": "#52514e",
    "neutral300": "#1f2328",
    "neutral400": "#6d6b67",
    "neutral500": "#f0eee6",
    "neutral600": "#bcd1ca"
  },
  "fonts": {
    "body": "'anthropicSans', sans-serif",
    "mono": "'anthropicMono', monospace"
  },
  "fontSizes": {
    "12": "12px",
    "13": "13px",
    "14": "14px",
    "15": "15px",
    "16": "16px",
    "18": "18px",
    "20": "20px",
    "22": "22px",
    "24": "24px",
    "26": "26px",
    "52": "52px"
  },
  "space": {
    "1": "1px",
    "20": "20px",
    "24": "24px",
    "28": "28px",
    "41": "41px",
    "46": "46px",
    "56": "56px",
    "64": "64px",
    "78": "78px",
    "89": "89px",
    "103": "103px",
    "115": "115px",
    "128": "128px",
    "139": "139px",
    "148": "148px",
    "164": "164px"
  },
  "radii": {
    "sm": "4px",
    "md": "10px",
    "lg": "14px"
  },
  "shadows": {
    "none": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px inset",
    "xs": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px inset, rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
    "lg": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 0px inset, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px, rgba(0, 0, 0, 0.12) 0px 8px 24px 0px, rgba(0, 0, 0, 0.08) 0px 2px 6px 0px",
    "xl": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.08) 0px 4px 8px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.08) 0px 12px 28px -2px"
  },
  "states": {
    "hover": {
      "opacity": 0.08
    },
    "focus": {
      "opacity": 0.12
    },
    "active": {
      "opacity": 0.16
    },
    "disabled": {
      "opacity": 0.38
    }
  }
};

// MUI v5 theme
export const muiTheme = {
  "palette": {
    "primary": {
      "main": "#cf222e",
      "light": "hsl(356, 72%, 62%)",
      "dark": "hsl(356, 72%, 32%)"
    },
    "secondary": {
      "main": "#0550ae",
      "light": "hsl(213, 94%, 50%)",
      "dark": "hsl(213, 94%, 20%)"
    },
    "background": {
      "default": "#fcfcfb",
      "paper": "#ffffff"
    },
    "text": {
      "primary": "#0b0b0b",
      "secondary": "#898781"
    }
  },
  "typography": {
    "fontFamily": "'anthropicSans', sans-serif",
    "h1": {
      "fontSize": "52px",
      "fontWeight": "300",
      "lineHeight": "57.2px"
    },
    "h2": {
      "fontSize": "24px",
      "fontWeight": "418.5",
      "lineHeight": "24px"
    },
    "h3": {
      "fontSize": "20px",
      "fontWeight": "400",
      "lineHeight": "30px"
    },
    "body1": {
      "fontSize": "18px",
      "fontWeight": "600",
      "lineHeight": "23.4px"
    }
  },
  "shape": {
    "borderRadius": 7
  },
  "shadows": [
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px inset",
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px inset, rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 0px inset, color(srgb 0.0431373 0.0431373 0.0431373 / 0.1) 0px 0px 0px 1px, rgba(0, 0, 0, 0.12) 0px 8px 24px 0px, rgba(0, 0, 0, 0.08) 0px 2px 6px 0px",
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.08) 0px 4px 8px 0px, color(srgb 0.0431373 0.0431373 0.0431373 / 0.08) 0px 12px 28px -2px"
  ]
};

export default theme;
