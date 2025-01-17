# BUILD NOTE:
# until we get binutils with https://sourceware.org/bugzilla/show_bug.cgi?id=28138 fixed
# build requires >1024 available file descriptors (4096 seems sufficient)
#
# TODO
# - unpackaged files
#   /usr/share/doc/node/gdbinit

# Conditional build:
%bcond_without	system_brotli	# system brotli
%bcond_without	system_uv	# system uv
%bcond_with	http_parser	# system http-parser and llhttp

%define		_enable_debug_packages	0

# NOTES:
# - https://nodejs.org/en/download/releases/

# NODE_MODULE_VERSION refers to the ABI (application binary interface) version
# number of Node.js, used to determine which versions of Node.js compiled C++
# add-on binaries can be loaded in to without needing to be re-compiled. It
# used to be stored as hex value in earlier versions, but is now represented as
# an integer.
%define		node_module_version	127
Summary:	Asynchronous JavaScript Engine
Summary(pl.UTF-8):	Asynchroniczny silnik JavaScriptu
Name:		nodejs
# 22.x LTS - https://github.com/nodejs/Release
# Active start: 2024-10-29
# Maintenance start: October 2025
# Maintenance end: April 2027
Version:	22.13.0
Release:	2
License:	BSD and MIT and Apache v2.0 and GPL v3
Group:		Development/Languages
Source0:	https://nodejs.org/download/release/latest-v22.x/node-v%{version}.tar.xz
# Source0-md5:	9313baec7c7be80305edb8e5b5c074c7
# force node to use /usr/lib/node as the systemwide module directory
Patch0:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch1:		%{name}-lib64path.patch
Patch2:		0001-Remove-unused-OpenSSL-config.patch
Patch3:		arm-yield.patch
URL:		https://nodejs.org/
BuildRequires:	c-ares-devel >= 1.17.2
BuildRequires:	gcc >= 6:6.3
%if %{with http_parser}
BuildRequires:	http-parser-devel >= 2.9.3
BuildRequires:	llhttp-devel >= 2.1.3
%endif
%ifarch mips mipsel mips64 mips64el ppc %{arm}
BuildRequires:	libatomic-devel
%endif
%{?with_system_brotli:BuildRequires:	libbrotli-devel >= 1.0.9}
BuildRequires:	libicu-devel >= 69.1
BuildRequires:	libstdc++-devel >= 6:4.8
%{?with_system_uv:BuildRequires:	libuv-devel >= 1.42.0}
BuildRequires:	nghttp2-devel >= 1.42.0
BuildRequires:	openssl-devel >= 1.0.1
BuildRequires:	pkgconfig
BuildRequires:	python3 >= 1:3.6
BuildRequires:	python3-modules >= 1:3.6
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.752
BuildRequires:	tar >= 1:1.22
BuildRequires:	sed >= 4.0
BuildRequires:	xz
BuildRequires:	zlib-devel >= 1.2.11
Requires:	c-ares >= 1.17.1
Requires:	ca-certificates
%{?with_http_parser:Requires:	http-parser >= 2.9.3}
%{?with_system_brotli:Requires:	libbrotli >= 1.0.9}
%{?with_system_uv:Requires:	libuv >= 1.42.0}
Requires:	nghttp2-libs >= 1.42.0
Requires:	zlib >= 1.2.11
Provides:	nodejs(engine) = %{version}
Provides:	nodejs(module-version) = %{node_module_version}
Obsoletes:	nodejs-waf < 0.9
Obsoletes:	systemtap-nodejs < 22.4.0
ExclusiveArch:	%{ix86} %{x8664} %{arm} aarch64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		sover	%(echo %{version} | cut -d. -f2)
# add macro, so adapter won't replace it back literal
%define		doc_ver	%{version}

%description
Node.js is a platform built on Chrome's JavaScript runtime for easily
building fast, scalable network applications. Node.js uses an
event-driven, non-blocking I/O model that makes it lightweight and
efficient, perfect for data-intensive real-time applications that run
across distributed devices.

%description -l pl.UTF-8
Node.js to platforma zbudowana w opacriu o silnik JavaScriptu
przeglądarki Chrome, służąca do tworzenia szybkich, skalowalnych
aplikacji sieciowych. Node.js wykorzystuje nieblokujący model
wejścia/wyjścia sterowany zdarzeniami, dzięki czemu jest lekki i
wydajny, dobrze nadający się do aplikacji przetwarzających duże
ilości danych w czasie rzeczywistym, uruchamianych na rozproszonych
urządzeniach.

%package devel
Summary:	Development headers for nodejs
Summary(pl.UTF-8):	Pliki nagłówkowe nodejs
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	gcc
%{?with_http_parser:Requires:	http-parser-devel >= 2.9.3}
Requires:	libstdc++-devel
%{?with_system_uv:Requires:	libuv-devel >= 1.42.0}
Requires:	openssl-devel
Requires:	zlib-devel >= 1.2.11

%description devel
Development headers for nodejs.

%description devel -l pl.UTF-8
Pliki nagłówkowe nodejs.

%package doc
Summary:	Documentation for Node.js engine
Summary(pl.UTF-8):	Dokumentacja silnika Node.js
Group:		Documentation
URL:		https://nodejs.org/dist/v%{doc_ver}/docs/api
BuildArch:	noarch

%description doc
Node.js is a server-side JavaScript environment that uses an
asynchronous event-driven model. Node's goal is to provide an easy way
to build scalable network programs.

This package contains the documentation for Node.js.

%description doc -l pl.UTF-8
Node.js to serwerowe środowisko JavaScriptu wykorzystujące
asynchroniczny model sterowany zdarzeniami. Celem Node jest
zapewnienie łatwego sposobu tworzenia skalowalnych programów
sieciowych.

Ten pakiet zawiera dokumentację Node.js.

%prep
%setup -q -n node-v%{version}
%if "%{_lib}" == "lib64"
%patch -P1 -p1
%else
%patch -P0 -p1
%endif
%patch -P2 -p1
%patch -P3 -p1

grep -r '#!.*env python' -l . | xargs %{__sed} -i -e '1 s,#!.*env python$,#!%{__python3},'

%{?with_system_brotli:%{__rm} -r deps/brotli}
%{__rm} -r deps/cares
%if %{with http_parser}
%{__rm} -r deps/http_parser
%{__rm} -r deps/llhttp
%endif
%{__rm} -r deps/icu-small
%{__rm} -r deps/nghttp2
%{__rm} -r deps/npm
%{__rm} -r deps/openssl
%{?with_system_uv:%{__rm} -r deps/uv}
%{__rm} -r deps/zlib

%build
ver=$(awk '/#define NODE_MODULE_VERSION [0-9]+/{print $3}' src/node_version.h)
test "$ver" = "%{node_module_version}"

# CC used only to detect if CC is clang, not used for compiling
CC="%{__cc}" \
CXX="%{__cxx}" \
GYP_DEFINES="soname_version=%{sover}" \
./configure \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--openssl-use-def-ca-store \
	--shared \
	%{?with_system_brotli:--shared-brotli} \
	--shared-cares \
	%{?with_http_parser:--shared-http-parser} \
	%{?with_system_uv:--shared-libuv} \
	--shared-nghttp2 \
	--shared-openssl \
	--shared-zlib \
	--with-intl=system-icu \
	--without-corepack \
	--without-npm

# add LFS defines from libuv (RHBZ#892601)
# CXXFLAGS must be exported, as it is needed for make, not gyp
CXXFLAGS="%{rpmcxxflags} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 -fPIC" \
LDFLAGS="%{rpmldflags}" \
PATH="$(pwd)/out/tools/bin:$PATH" \
%{__make} -C out \
	BUILDTYPE=Release \
	V=1

%install
rm -rf $RPM_BUILD_ROOT

%{__python3} tools/install.py --dest-dir "$RPM_BUILD_ROOT" --prefix "%{_prefix}" install

ln -s libnode.so.%{node_module_version} $RPM_BUILD_ROOT%{_libdir}/libnode.so

echo '.so man1/node.1' > $RPM_BUILD_ROOT%{_mandir}/man1/nodejs.1

install -d $RPM_BUILD_ROOT%{_includedir}/node
cp -p src/*.h $RPM_BUILD_ROOT%{_includedir}/node

# install for node-gyp
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{name}
cp -p common.gypi $RPM_BUILD_ROOT%{_usrsrc}/%{name}
ln -s %{_includedir}/node $RPM_BUILD_ROOT%{_usrsrc}/%{name}/src

# for compat of fedora derivered scripts (shebangs)
ln -s node $RPM_BUILD_ROOT%{_bindir}/nodejs

# globally installed node modules (noarch)
install -d $RPM_BUILD_ROOT%{_prefix}/lib/node_modules

# default searchpaths
install -d $RPM_BUILD_ROOT{%{_libdir},%{_prefix}/lib}/node

# create pkgconfig
install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
cat <<'EOF' > $RPM_BUILD_ROOT%{_pkgconfigdir}/%{name}.pc
version=%{version}
prefix=%{_prefix}
libdir=${prefix}/%{_lib}
includedir=${prefix}/include/node

Name: nodejs
Description: Evented I/O for V8 JavaScript.
Version: ${version}
Cflags: -I${includedir}
EOF

# install documentation
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
cp -a doc/api/* $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.md
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.json

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE GOVERNANCE.md README.md SECURITY.md
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/nodejs
%attr(755,root,root) %{_libdir}/libnode.so.%{node_module_version}
%if "%{_lib}" != "lib"
%dir %{_libdir}/node
%endif
%dir %{_prefix}/lib/node
%dir %{_prefix}/lib/node_modules
%{_mandir}/man1/node.1*
%{_mandir}/man1/nodejs.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnode.so
%{_includedir}/node
%{_pkgconfigdir}/nodejs.pc
%{_usrsrc}/%{name}

%files doc
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-doc-%{version}
