# TODO
# - unpackaged files
#   /usr/share/doc/node/gdbinit

# Conditional build:
%bcond_without	system_uv	# system uv
%bcond_with	shared		# build libnode.so shared library

# NOTES:
# - https://nodejs.org/en/download/releases/

# NODE_MODULE_VERSION refers to the ABI (application binary interface) version
# number of Node.js, used to determine which versions of Node.js compiled C++
# add-on binaries can be loaded in to without needing to be re-compiled. It
# used to be stored as hex value in earlier versions, but is now represented as
# an integer.
%define		node_module_version	64
Summary:	Asynchronous JavaScript Engine
Summary(pl.UTF-8):	Asynchroniczny silnik JavaScriptu
Name:		nodejs
# 10.x LTS - https://github.com/nodejs/Release
# Active start: 2018-10-30
# Maintenance start: April 2020
# Maintenance end: April 2021
Version:	10.16.0
Release:	1
License:	BSD and MIT and Apache v2.0 and GPL v3
Group:		Development/Languages
Source0:	https://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz
# Source0-md5:	46f47630e088540968962f1ad71b9d0a
Patch1:		%{name}-shared.patch
# force node to use /usr/lib/node as the systemwide module directory
Patch2:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch3:		%{name}-lib64path.patch
Patch5:		uv-fpic.patch
URL:		https://nodejs.org/
BuildRequires:	gcc >= 6:4.8
BuildRequires:	http-parser-devel >= 2.9.2
BuildRequires:	libstdc++-devel >= 6:4.8
%{?with_system_uv:BuildRequires:	libuv-devel >= 1.29.0}
BuildRequires:	openssl-devel >= 1.0.1
BuildRequires:	pkgconfig
BuildRequires:	python >= 1:2.7
BuildRequires:	python-jsmin
BuildRequires:	python-modules >= 1:2.7
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	sed >= 4.0
BuildRequires:	zlib-devel
Requires:	ca-certificates
Provides:	nodejs(engine) = %{version}
Provides:	nodejs(module-version) = %{node_module_version}
Obsoletes:	nodejs-waf
ExclusiveArch:	%{ix86} %{x8664} arm
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
Requires:	http-parser-devel >= 2.9.2
Requires:	libstdc++-devel
%{?with_system_uv:Requires:	libuv-devel >= 1.29.0}
Requires:	openssl-devel
Requires:	zlib-devel

%description devel
Development headers for nodejs.

%description devel -l pl.UTF-8
Pliki nagłówkowe nodejs.

%package doc
Summary:	Documentation for Node.js engine
Summary(pl.UTF-8):	Dokumentacja silnika Node.js
Group:		Documentation
URL:		https://nodejs.org/dist/v%{doc_ver}/docs/api
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

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

%package -n systemtap-nodejs
Summary:	systemtap/dtrace probes for Node.js
Summary(pl.UTF-8):	Sondy systemtap/dtrace dla Node.js
Group:		Development/Tools
Requires:	%{name} = %{version}-%{release}
Requires:	systemtap-client

%description -n systemtap-nodejs
systemtap/dtrace probes for Node.js.

%description -n systemtap-nodejs -l pl.UTF-8
Sondy systemtap/dtrace dla Node.js.

%prep
%setup -q -n node-v%{version}
%{?with_shared:%patch1 -p1}
#%patch1 -p1
%if %{_lib} == "lib64"
%patch3 -p1
%else
%patch2 -p1
%endif
#%{?with_system_uv:%patch5 -p1}

grep -r '#!.*env python' -l . | xargs %{__sed} -i -e '1 s,#!.*env python,#!%{__python},'

%{__rm} -r deps/npm
%{__rm} -r deps/http_parser
%{__rm} -r deps/openssl
%{?with_system_uv:%{__rm} -r deps/uv}
%{__rm} -r deps/zlib

%build
ver=$(awk '/#define NODE_MODULE_VERSION/{print $3}' src/node_version.h)
test "$ver" = "%{node_module_version}"

# CC used only to detect if CC is clang, not used for compiling
CC="%{__cc}" \
CXX="%{__cxx}" \
GYP_DEFINES="soname_version=%{sover}" \
./configure \
	--openssl-use-def-ca-store \
	%{?0:--shared-cares} \
	--shared-openssl \
	--shared-http-parser \
	%{?with_system_uv:--shared-libuv} \
	--shared-zlib \
	--without-npm \
	--without-dtrace \
	--prefix=%{_prefix}

# add LFS defines from libuv (RHBZ#892601)
# CXXFLAGS must be exported, as it is needed for make, not gyp
CXXFLAGS="%{rpmcxxflags} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 -fPIC" \
LDFLAGS="%{rpmldflags}" \
%{__make} -C out \
	BUILDTYPE=Release \
	V=1

%install
rm -rf $RPM_BUILD_ROOT

%{__python} tools/install.py install "$RPM_BUILD_ROOT" "%{_prefix}"

%if %{with shared}
lib=$(basename $RPM_BUILD_ROOT%{_libdir}/libnode.so.*.*.*)
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so.10
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so
%endif

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

%if %{with shared}
%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig
%endif

%files
%defattr(644,root,root,755)
%doc README.md AUTHORS CHANGELOG.md LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/nodejs
%if %{with shared}
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libnode.so.10
%endif
%if "%{_lib}" != "lib"
%dir %{_libdir}/node
%endif
%dir %{_prefix}/lib/node
%dir %{_prefix}/lib/node_modules
%{_mandir}/man1/node.1*
%{_mandir}/man1/nodejs.1*

%files devel
%defattr(644,root,root,755)
%if %{with shared}
%attr(755,root,root) %{_libdir}/libnode.so
%endif
%{_includedir}/node
%{_pkgconfigdir}/nodejs.pc
%{_usrsrc}/%{name}

%files doc
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-doc-%{version}

%files -n systemtap-nodejs
%defattr(644,root,root,755)
%{_datadir}/systemtap/tapset/node.stp
